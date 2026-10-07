import json
from datetime import date
import pandas as pd
from streamlit.testing.v1 import AppTest
from config import ROOT
from native_access import available_sources, connect_source, conditions

baseline = pd.read_csv(ROOT / 'data/sales.csv', parse_dates=['order_date'])
columns = ', '.join(baseline.columns)
report = {'status': 'passed', 'sources': {}, 'checks': ['all rows match CSV', 'SQL totals match pandas', 'region filter', 'date filter', 'empty filter', 'dashboard rendering', 'partition pruning']}
for source in available_sources():
    with connect_source(source) as con:
        frame = con.execute(f'SELECT {columns} FROM sales ORDER BY order_id').df()
        pd.testing.assert_frame_equal(baseline, frame, check_dtype=False)
        total = con.execute('SELECT sum(revenue) FROM sales').fetchone()[0]
        assert abs(total - baseline.revenue.sum()) < .001
        expected = len(baseline[baseline.region == 'South'])
        assert con.execute("SELECT count(*) FROM sales WHERE region = 'South'").fetchone()[0] == expected
        january = baseline[baseline.order_date.dt.month == 1]
        assert con.execute("SELECT count(*) FROM sales WHERE order_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31'").fetchone()[0] == len(january)
        if 'partitioned' in source or 'HDFS Parquet' in source:
            where, params = conditions(sorted(baseline.region.unique()), sorted(baseline.category.unique()), (date(2026, 1, 1), date(2026, 6, 29)), [1])
            plan = con.execute(f'EXPLAIN ANALYZE SELECT sum(revenue) FROM sales WHERE {where}', params).fetchone()[1]
            assert 'Total Files Read: 1' in plan and 'File Filters:' in plan, plan
            constant_plan = con.execute('EXPLAIN ANALYZE SELECT sum(revenue) FROM sales WHERE year=2026 AND month=1').fetchone()[1]
            assert 'Scanning Files: 1/6' in constant_plan, constant_plan
            (ROOT / ('plan-hdfs.txt' if 'HDFS' in source else 'plan-linux.txt')).write_text('Dashboard parameters:\n' + plan + '\nConstant partition filter:\n' + constant_plan)
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120).run()
    app.sidebar.selectbox[0].select(source).run()
    assert not app.exception and not app.error, (app.exception, app.error)
    assert app.metric[0].value == '5,000'
    app.sidebar.date_input[0].set_value((date(2026, 1, 1), date(2026, 1, 31))).run()
    assert not app.exception and not app.error
    assert int(app.metric[0].value.replace(',', '')) == len(january)
    app.sidebar.date_input[0].set_value((date(2026, 1, 1), date(2026, 6, 29))).run()
    if 'partitioned' in source or 'HDFS Parquet' in source:
        app.sidebar.multiselect[2].set_value([1]).run()
        assert not app.exception and not app.error
        assert int(app.metric[0].value.replace(',', '')) == len(january)
        app.sidebar.multiselect[2].set_value(list(range(1, 7))).run()
    app.sidebar.multiselect[0].set_value(['South']).run()
    assert not app.exception and not app.error
    assert int(app.metric[0].value.replace(',', '')) == expected
    app.sidebar.multiselect[0].set_value([]).run()
    assert not app.exception and not app.error and len(app.info) == 1
    report['sources'][source] = {'status': 'passed', 'rows': len(frame), 'revenue': round(total, 2)}
    print(source, 'passed', flush=True)
(ROOT / 'validation-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
