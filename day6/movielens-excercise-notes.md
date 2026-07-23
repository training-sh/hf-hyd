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
