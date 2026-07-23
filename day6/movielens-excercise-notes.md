DataSet link  https://grouplens.org/datasets/movielens/


33,000,000 ratings , 86K movies data set

Download ml-latest.zip (size: 335 MB)  https://files.grouplens.org/datasets/movielens/ml-latest.zip

Try to do timeit module for two approach.

-- Perform movies join with ratings. then perform aggregation. check time
-- Perform ratings analytics with agg, filter for rating 4.0 and above, rated by at least 4000 users, then Join with movies, check time




to convert long timestamp in sec to datetime 

df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

After completion,

- write the results as popular-movies.json and
- - popular-movies.csv using pandas write

```

NO DATA INFERENCE

movies
define shcema for movies

load using pandas

ratings - load using pandas, with defined schema

import logging 

try to write to logs 

log.debug("loading movies.sv")
load the file
log.info("loaded movies csv")

write total records into logs as info 

..

rating, we have timestamp in seconds since 1970
convert this into pandas date time 

find popular movies on ratings on pandas 
    avg ratings >= 4.0 and numner of ratings > 100 - for small data set 


join the popular movies with movies panda df to get movie title, genres

--

````
