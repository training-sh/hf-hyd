quick example, make your own changes to get start with moviedata..

```
show stages;

CREATE STAGE IF NOT EXISTS my_stage
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'stage hello world demo';

LIST @my_stage;


CREATE FILE FORMAT my_csv_format
TYPE = CSV
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"';

SELECT
    $1,
    $2,
    $3
FROM @my_stage/movies.csv
(FILE_FORMAT => my_csv_format);

-- $3::NUMBER     AS rating

SELECT
    $1::INT        AS movie_id,
    $2::STRING     AS title,
    $3::STRING     AS genre
FROM @my_stage/movies.csv
(FILE_FORMAT => my_csv_format);


CREATE OR REPLACE TABLE movies AS
SELECT
    $1::INT     AS movie_id,
    $2::STRING  AS title,
    $3::STRING  AS genres
FROM @my_stage/movies.csv
(FILE_FORMAT => my_csv_format);


SELECT * FROM movies LIMIT 10;

CREATE OR REPLACE TABLE movies2 (
    movie_id INT,
    title    STRING,
    genres   STRING
);

COPY INTO movies
FROM @my_stage/movies.csv
FILE_FORMAT = (FORMAT_NAME = my_csv_format);
```



```
-- Create a basic internal stage
CREATE OR REPLACE STAGE my_internal_stage
  FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1)
  COMMENT = 'Internal stage for CSV data uploads';

```

```
-- Create an external stage pointing to a cloud storage bucket
CREATE OR REPLACE STAGE my_external_s3_stage
  URL = 's3://my-company-bucket/incoming/data/'
  STORAGE_INTEGRATION = my_s3_storage_integration
  FILE_FORMAT = (TYPE = 'JSON');
```
