"""File-level schema drift and write reconciliation for Spark and Iceberg."""
import getpass
import hashlib
import socket
import uuid
from datetime import datetime, timezone
from functools import reduce
from pyspark import StorageLevel
from pyspark.sql import functions as F, types as T

PROVENANCE = ('_batch_id', '_run_id', '_source_file')
CORRUPT = '_corrupt_record'
RAW = '__raw_record'
AUDIT_DDL = """drift_id STRING, run_id STRING, batch_id STRING, detected_at TIMESTAMP,
dataset_name STRING, source_format STRING, source_path STRING, source_file_path STRING,
source_file_name STRING, file_size_bytes BIGINT, file_modified_at TIMESTAMP,
file_count BIGINT, file_names ARRAY<STRING>, target_catalog STRING,
target_namespace STRING, target_table STRING, expected_schema STRING, actual_schema STRING,
drift_detected BOOLEAN, drift_types ARRAY<STRING>, added_columns ARRAY<STRING>,
missing_columns ARRAY<STRING>, type_changed_columns ARRAY<STRING>, record_count BIGINT,
good_record_count BIGINT, bad_record_count BIGINT, bronze_written_count BIGINT,
quarantine_written_count BIGINT, reconciliation_status STRING, reconciliation_error STRING,
reconciled_at TIMESTAMP, quarantine_file_path STRING, processing_error STRING,
action_taken STRING, status STRING, spark_app_id STRING, spark_app_name STRING,
execution_user STRING, host_name STRING, notebook_name STRING, created_at TIMESTAMP"""
BAD_SCHEMA = T.StructType([
    T.StructField(name, T.StringType(), True) for name in PROVENANCE
] + [T.StructField('source_record_json', T.StringType(), True),
     T.StructField('error_columns', T.ArrayType(T.StringType()), True),
     T.StructField('error_reasons', T.ArrayType(T.StringType()), True)])


def utc_now():
    """Return a runtime UTC timestamp, independent of the host timezone."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ident(name):
    """Quote a Spark SQL identifier safely."""
    return '`' + name.replace('`', '``') + '`'


def table_id(catalog, namespace, table):
    return '.'.join(map(ident, (catalog, namespace, table)))


def ensure_namespace_exists(spark, catalog_name, namespace_name):
    """Create an Iceberg namespace only if absent."""
    spark.sql(f'CREATE NAMESPACE IF NOT EXISTS {ident(catalog_name)}.{ident(namespace_name)}')


def schema_ddl(schema):
    return ', '.join(f'{ident(f.name)} {f.dataType.simpleString()}' +
                     ('' if f.nullable else ' NOT NULL') for f in schema)


def ensure_table_exists(spark, catalog_name, namespace_name, table_name, schema_definition):
    """Create an Iceberg table without replacing an existing table."""
    ensure_namespace_exists(spark, catalog_name, namespace_name)
    ddl = schema_ddl(schema_definition) if isinstance(schema_definition, T.StructType) else schema_definition
    spark.sql(f'CREATE TABLE IF NOT EXISTS {table_id(catalog_name, namespace_name, table_name)} '
              f'({ddl}) USING iceberg')


def ensure_columns(spark, target, required_schema):
    """Add missing metadata columns; fail on incompatible existing column types."""
    existing = {f.name: f.dataType for f in spark.table(target).schema}
    for field in required_schema:
        if field.name not in existing:
            spark.sql(f'ALTER TABLE {target} ADD COLUMN {ident(field.name)} {field.dataType.simpleString()}')
        elif existing[field.name] != field.dataType:
            raise ValueError(f'Incompatible metadata type: {target}.{field.name}')


def ensure_audit_table(spark, catalog_name, namespace_name='operations', table_name='schema_drift'):
    """Create/extend the audit schema; historical batch rows are not converted to file rows."""
    ensure_table_exists(spark, catalog_name, namespace_name, table_name, AUDIT_DDL)
    # Spark parses the DDL, with no Python type inference or data processing.
    required = spark.createDataFrame([], AUDIT_DDL).schema
    ensure_columns(spark, table_id(catalog_name, namespace_name, table_name), required)


def list_source_files(spark, source_path):
    """Inventory Hadoop filesystem paths, including empty and unreadable data files."""
    jvm = spark._jvm
    path = jvm.org.apache.hadoop.fs.Path(source_path)
    fs = path.getFileSystem(spark._jsc.hadoopConfiguration())
    matches = fs.globStatus(path)
    if matches is None or not len(matches):
        raise FileNotFoundError(source_path)
    files = {}

    def add(status):
        current = status.getPath()
        name = current.getName()
        if name.startswith(('.', '_')):
            return
        if status.isDirectory():
            for child in fs.listStatus(current):
                add(child)
        else:
            uri = fs.makeQualified(current).toString()
            files[uri] = dict(source_file_path=uri, source_file_name=name,
                              file_size_bytes=int(status.getLen()),
                              file_modified_at=datetime.fromtimestamp(
                                  status.getModificationTime() / 1000, timezone.utc).replace(tzinfo=None))
    for match in matches:
        add(match)
    if not files:
        raise ValueError('No visible source files found; no file audit rows can be created')
    return [files[key] for key in sorted(files)]


def file_signature(spark, source_path):
    path = spark._jvm.org.apache.hadoop.fs.Path(source_path)
    status = path.getFileSystem(spark._jsc.hadoopConfiguration()).getFileStatus(path)
    return int(status.getLen()), int(status.getModificationTime())


def path_exists(spark, source_path):
    path = spark._jvm.org.apache.hadoop.fs.Path(source_path)
    return path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(path)


def read_source_batch(spark, source_path, source_format, options=None):
    """Read one file with its own schema; keep parse failures as corrupt records."""
    fmt = source_format.lower()
    if fmt not in ('csv', 'json', 'jsonl', 'parquet'):
        raise ValueError(f'Unsupported format: {fmt}')
    options = dict(options or {})
    for option in ('ignoreCorruptFiles', 'ignoreMissingFiles'):
        if str(options.get(option, 'false')).lower() == 'true':
            raise ValueError(f'{option}=true would silently lose records; file failures must be audited')
    if fmt == 'parquet':
        return spark.read.options(**options).parquet(source_path)
    if str(options.get('mode', 'PERMISSIVE')).upper() != 'PERMISSIVE':
        raise ValueError('Use PERMISSIVE mode to retain malformed source records')
    if str(options.get('samplingRatio', '1.0')) != '1.0':
        raise ValueError('Use samplingRatio=1.0 for a complete file-schema inference')
    defaults = dict(mode='PERMISSIVE', columnNameOfCorruptRecord=CORRUPT, samplingRatio='1.0')
    if fmt == 'csv':
        defaults.update(header='true', inferSchema='true', enforceSchema='false')
    else:
        defaults.update(multiLine='false' if fmt == 'jsonl' else 'true')
    defaults.update(options)
    defaults['columnNameOfCorruptRecord'] = CORRUPT
    fmt = 'json' if fmt == 'jsonl' else fmt
    inferred = spark.read.format(fmt).options(**defaults).load(source_path).schema
    if CORRUPT not in inferred.names:
        inferred = T.StructType(inferred.fields + [T.StructField(CORRUPT, T.StringType(), True)])
    if source_format.lower() == 'jsonl':
        # Parse text lines explicitly so even an entirely malformed file is quarantineable.
        # Direct Spark JSON scans forbid queries selecting only the corrupt-record column.
        lines = spark.read.text(source_path).where(F.length(F.trim('value')) > 0)
        return lines.select(F.from_json('value', inferred, defaults).alias('parsed'),
                            F.col('value').alias(RAW)).select('parsed.*', RAW)
    return spark.read.format(fmt).schema(inferred).options(**defaults).load(source_path)


def business_schema(schema):
    """Exclude parser/provenance metadata from schema drift comparison."""
    return T.StructType([f for f in schema if f.name not in (*PROVENANCE, CORRUPT, RAW)])


def compare_schemas(expected_schema, actual_schema):
    """Compare file-level top-level names/types, ignoring column order."""
    expected = {f.name: f.dataType for f in expected_schema}
    actual = {f.name: f.dataType for f in actual_schema}
    added = sorted(actual.keys() - expected.keys())
    missing = sorted(expected.keys() - actual.keys())
    changed = [f'{name}: {expected[name].simpleString()} -> {actual[name].simpleString()}'
               for name in sorted(expected.keys() & actual.keys()) if expected[name] != actual[name]]
    kinds = [kind for kind, values in [('NEW_COLUMN', added), ('MISSING_COLUMN', missing),
                                      ('TYPE_CHANGED', changed)] if values]
    return dict(drift_detected=bool(kinds), drift_types=kinds, added_columns=added,
                missing_columns=missing, type_changed_columns=changed)


def align_records(df, expected, batch_id=None, run_id=None, source_file=None):
    """Split compatible rows and original JSON records with column-specific errors."""
    expressions, errors, columns = [], [], []
    actual = {f.name: f.dataType for f in df.schema}

    def error(condition, name, message):
        errors.append(F.when(condition, F.lit(message)))
        columns.append(F.when(condition, F.lit(name)))

    if CORRUPT in actual:
        error(F.col(ident(CORRUPT)).isNotNull(), CORRUPT, 'MALFORMED_RECORD: parser could not read this record')
    for field in expected:
        name, dtype = field.name, field.dataType
        if name not in actual:
            value = F.lit(None).cast(dtype)
            if not field.nullable:
                error(F.lit(True), name, f'MISSING_REQUIRED_COLUMN: {name}')
        else:
            original = F.col(ident(name))
            if actual[name] == dtype:
                value = original
            elif isinstance(dtype, (T.StructType, T.ArrayType, T.MapType)) or isinstance(
                    actual[name], (T.StructType, T.ArrayType, T.MapType)):
                value = F.lit(None).cast(dtype)
                error(F.lit(True), name, f'UNSUPPORTED_COMPLEX_TYPE_CHANGE: {name}')
            else:
                value = F.expr(f'try_cast({ident(name)} AS {dtype.simpleString()})')
                error(original.isNotNull() & value.isNull(), name,
                      f'INVALID_CAST: {name} cannot convert to {dtype.simpleString()}')
            if not field.nullable:
                error(original.isNull(), name, f'NULL_REQUIRED_VALUE: {name}')
        expressions.append(value.alias(name))
    empty = F.array().cast('array<string>')
    error_list = F.filter(F.array(*errors), lambda item: item.isNotNull()) if errors else empty
    column_list = F.filter(F.array(*columns), lambda item: item.isNotNull()) if columns else empty
    marked = df.withColumn('__drift_errors', error_list).withColumn('__drift_columns', column_list)
    metadata = [F.lit(value).cast('string').alias(name) for name, value in
                zip(PROVENANCE, (batch_id, run_id, source_file))]
    good = marked.where(F.size('__drift_errors') == 0).select(*expressions, *metadata)
    original_json = F.to_json(F.struct(*[F.col(ident(name)).alias(name) for name in df.columns]),
                             options={'ignoreNullFields': 'false'})
    bad = marked.where(F.size('__drift_errors') > 0).select(
        *metadata, original_json.alias('source_record_json'),
        F.col('__drift_columns').alias('error_columns'), F.col('__drift_errors').alias('error_reasons'))
    return good, bad


def write_audit_to_iceberg(spark, audit_record, catalog_name,
                           namespace_name='operations', table_name='schema_drift'):
    """Append exactly one file audit dictionary using the explicit Iceberg schema."""
    ensure_audit_table(spark, catalog_name, namespace_name, table_name)
    target = table_id(catalog_name, namespace_name, table_name)
    spark.createDataFrame([audit_record], spark.table(target).schema).writeTo(target).append()


def reconcile_file(spark, target, quarantine_file_path, audit):
    """Read persisted destinations and compare their file-scoped counts to the split."""
    result = dict(bronze_written_count=None, quarantine_written_count=None,
                  reconciliation_status='FAILED', reconciliation_error=None, reconciled_at=utc_now())
    errors = []
    try:
        result['bronze_written_count'] = spark.table(target).where(
            (F.col('_batch_id') == audit['batch_id']) &
            (F.col('_run_id') == audit['run_id']) &
            (F.col('_source_file') == audit['source_file_path'])).count()
    except Exception as exc:
        errors.append(f'Bronze verification failed: {exc}')
    try:
        if path_exists(spark, quarantine_file_path):
            persisted = spark.read.parquet(quarantine_file_path)
            result['quarantine_written_count'] = persisted.where(
                (F.col('_batch_id') == audit['batch_id']) &
                (F.col('_run_id') == audit['run_id']) &
                (F.col('_source_file') == audit['source_file_path'])).count()
        else:
            result['quarantine_written_count'] = 0
    except Exception as exc:
        errors.append(f'Quarantine verification failed: {exc}')
    expected = [audit[key] for key in ('record_count', 'good_record_count', 'bad_record_count')]
    if any(value is None for value in expected):
        errors.append('Source/split counts are unknown; reconciliation cannot be verified')
        if result['bronze_written_count'] is not None and result['quarantine_written_count'] is not None:
            result['reconciliation_status'] = 'NOT_VERIFIABLE'
    else:
        total, good, bad = expected
        if total != good + bad:
            errors.append('Source count differs from correct + bad record counts')
        if result['bronze_written_count'] != good:
            errors.append('Persisted Bronze count differs from correct record count')
        if result['quarantine_written_count'] != bad:
            errors.append('Persisted quarantine count differs from bad record count')
    if audit['processing_error']:
        errors.append('Processing failed; persisted counts do not establish a successful ingestion')
    if not errors:
        result['reconciliation_status'] = 'RECONCILED'
    result['reconciliation_error'] = '\n'.join(errors) if errors else None
    return result


def batch_summary_query(catalog_name='datalake'):
    """Summarize file audit rows; preserve unknown counts instead of treating them as zero."""
    audit = table_id(catalog_name, 'operations', 'schema_drift')
    counts = ',\n'.join(f'CASE WHEN COUNT({name}) = COUNT(*) THEN SUM({name}) END AS {name}'
                        for name in ('record_count', 'good_record_count', 'bad_record_count',
                                     'bronze_written_count', 'quarantine_written_count'))
    return f'''SELECT run_id, batch_id, dataset_name, target_catalog, target_namespace, target_table,
        COUNT(*) AS file_count, {counts},
        SUM(CASE WHEN drift_detected THEN 1 ELSE 0 END) AS drift_file_count,
        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_file_count,
        SUM(CASE WHEN reconciliation_status = 'RECONCILED' THEN 1 ELSE 0 END) AS reconciled_file_count,
        CASE WHEN SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) > 0 THEN 'FAILED'
             WHEN SUM(CASE WHEN status = 'WARNING' THEN 1 ELSE 0 END) > 0 THEN 'WARNING'
             ELSE 'SUCCESS' END AS status,
        CASE WHEN SUM(CASE WHEN reconciliation_status = 'RECONCILED' THEN 1 ELSE 0 END) = COUNT(*)
             THEN 'RECONCILED' ELSE 'FAILED' END AS reconciliation_status
        FROM {audit} WHERE source_file_path IS NOT NULL
        GROUP BY run_id, batch_id, dataset_name, target_catalog, target_namespace, target_table'''


def create_batch_summary_view(spark, catalog_name='datalake', view_name='schema_drift_batch_summary'):
    """Register a session view; the Hadoop catalog does not require persistent view support."""
    spark.sql(f'CREATE OR REPLACE TEMP VIEW {ident(view_name)} AS {batch_summary_query(catalog_name)}')


def _process_batch(spark, dataset_name, source_path, source_format, target_catalog,
                   target_namespace, target_table, expected_schema=None, reader_options=None,
                   notebook_name=None, quarantine_path=None, batch_id=None, cache_enabled=True):
    """Process files independently, keeping one shared batch ID and one audit per file."""
    if not quarantine_path:
        raise ValueError('Provide quarantine_path to retain bad records')
    spark.conf.set('spark.sql.caseSensitive', 'true')
    spark.conf.set('spark.sql.csv.parser.columnPruning.enabled', 'false')
    files = list_source_files(spark, source_path)
    run_id = str(uuid.uuid4())
    batch_id = batch_id or f'{dataset_name}_{uuid.uuid4().hex}'
    ensure_audit_table(spark, target_catalog)
    audit_target = table_id(target_catalog, 'operations', 'schema_drift')
    if spark.table(audit_target).where((F.col('batch_id') == batch_id) &
                                     (F.col('dataset_name') == dataset_name)).limit(1).count():
        raise ValueError('This dataset/batch_id is already audited; inspect persisted destinations before retrying')
    target = table_id(target_catalog, target_namespace, target_table)
    if spark.catalog.tableExists(target):
        expected_schema = business_schema(spark.table(target).schema)
    elif expected_schema is None:
        raise ValueError('First load requires an expected StructType')
    reserved = set(PROVENANCE) | {CORRUPT, RAW, '__drift_errors', '__drift_columns'}
    if reserved.intersection(expected_schema.names):
        raise ValueError('Business schema contains reserved framework column names')
    target_schema = T.StructType(expected_schema.fields + [T.StructField(name, T.StringType(), True)
                                                          for name in PROVENANCE])
    ensure_table_exists(spark, target_catalog, target_namespace, target_table, target_schema)
    ensure_columns(spark, target, T.StructType(target_schema.fields[-3:]))
    audits, correct_frames, bad_frames = [], [], []
    for file in files:
        now = utc_now()
        qpath = quarantine_path.rstrip('/') + '/' + hashlib.sha256(batch_id.encode()).hexdigest()[:24]
        qpath += '/' + hashlib.sha256(file['source_file_path'].encode()).hexdigest()[:24]
        audit = dict(drift_id=str(uuid.uuid4()), run_id=run_id, batch_id=batch_id,
            detected_at=now, dataset_name=dataset_name, source_format=source_format,
            source_path=source_path, **file, file_count=1, file_names=[file['source_file_path']],
            target_catalog=target_catalog, target_namespace=target_namespace, target_table=target_table,
            expected_schema=expected_schema.json(), actual_schema=None, drift_detected=False,
            drift_types=[], added_columns=[], missing_columns=[], type_changed_columns=[],
            record_count=None, good_record_count=None, bad_record_count=None,
            bronze_written_count=None, quarantine_written_count=None, reconciliation_status=None,
            reconciliation_error=None, reconciled_at=None, quarantine_file_path=qpath,
            processing_error=None, action_taken='REJECTED', status='FAILED',
            spark_app_id=spark.sparkContext.applicationId, spark_app_name=spark.sparkContext.appName,
            execution_user=getpass.getuser(), host_name=socket.gethostname(),
            notebook_name=notebook_name, created_at=now)
        cached_frames = []
        try:
            before = file_signature(spark, file['source_file_path'])
            incoming = read_source_batch(spark, file['source_file_path'], source_format, reader_options)
            if cache_enabled:
                incoming.persist(StorageLevel.MEMORY_AND_DISK)
                cached_frames.append(incoming)
            if (set(incoming.columns) - {CORRUPT, RAW}).intersection(reserved):
                raise ValueError('Source file uses reserved framework column names')
            actual = business_schema(incoming.schema)
            audit['actual_schema'] = actual.json()
            audit.update(compare_schemas(expected_schema, actual))
            good, bad = align_records(incoming, expected_schema, batch_id, run_id, file['source_file_path'])
            if cache_enabled:
                for frame in (good, bad):
                    frame.persist(StorageLevel.MEMORY_AND_DISK)
                    cached_frames.append(frame)
            audit['record_count'] = incoming.count()
            audit['good_record_count'], audit['bad_record_count'] = good.count(), bad.count()
            # These frames describe the validated input split, even if a destination write fails.
            correct_frames.append(good)
            bad_frames.append(bad)
            if audit['bad_record_count']:
                bad.write.mode('errorifexists').parquet(qpath)
            if audit['good_record_count']:
                good.writeTo(target).append()
            if before != file_signature(spark, file['source_file_path']):
                raise RuntimeError('Source file changed during processing; reconciliation is unsafe')
            if audit['bad_record_count']:
                audit['action_taken'] = 'PARTIAL_ACCEPT' if audit['good_record_count'] else 'QUARANTINED'
                audit['status'] = 'WARNING' if audit['good_record_count'] else 'FAILED'
            else:
                audit['action_taken'] = 'ACCEPTED_WITH_DRIFT' if audit['drift_detected'] else 'ACCEPTED'
                audit['status'] = 'WARNING' if audit['drift_detected'] else 'SUCCESS'
        except Exception as exc:
            audit['processing_error'] = f'{type(exc).__name__}: {exc}'
            audit.update(action_taken='REJECTED', status='FAILED')
        finally:
            # Release each file's input and split caches on success or processing failure.
            for frame in reversed(cached_frames):
                frame.unpersist(blocking=True)
        audit.update(reconcile_file(spark, target, qpath, audit))
        if audit['reconciliation_status'] != 'RECONCILED':
            audit['status'] = 'FAILED'
        # An audit-write failure stops the batch rather than silently claiming success.
        write_audit_to_iceberg(spark, audit, target_catalog)
        audits.append(audit)
    create_batch_summary_view(spark, target_catalog)
    summary = spark.table('schema_drift_batch_summary').where(F.col('run_id') == run_id).first().asDict()
    def combine(frames, schema):
        return reduce(lambda left, right: left.unionByName(right), frames) if frames else spark.createDataFrame([], schema)
    return dict(summary=summary, file_audits=audits,
                correct_records=combine(correct_frames, target_schema),
                bad_records=combine(bad_frames, BAD_SCHEMA), spark_version=spark.version)


def process_csv_batch(spark, cache_enabled=True, **config):
    """Process CSV files with individual schema/error audits and a shared batch ID."""
    return _process_batch(spark, source_format='csv', cache_enabled=cache_enabled, **config)


def process_jsonl_batch(spark, cache_enabled=True, **config):
    """Process JSONL files with individual schema/error audits and a shared batch ID."""
    return _process_batch(spark, source_format='jsonl', cache_enabled=cache_enabled, **config)


def process_parquet_batch(spark, cache_enabled=True, **config):
    """Process Parquet files with individual schema/error audits and a shared batch ID."""
    return _process_batch(spark, source_format='parquet', cache_enabled=cache_enabled, **config)
