- First half day cover spark streaming introduction
- Spark Streaming hands-on with Ecomm data
- Second half, we will continue airflow with map-reduce, yarn, spark submit over WSL


File rename fix for hdfs/rename space with -

```
for f in *" "*; do mv -- "$f" "${f// /-}"; done
```

notes..

```


(apple, 2) <-- event <--
(apple, 3) <--
(orange, 1) <--
(apple, 1)

df.filter (name == 'apple')  <--  stateless
	(apple, 2)
	(apple, 3)


df.groupBy(name)
	.sum(value) <-- stateful function

state calculation 




apple   5 (old value 2) <-- inserted for (apple, 2) event, new result now apple is 5, updated for (apple, 3) event, updated for (apple, 1)
orange  1  <-- insert

State table in memory internally (insert/update)
apple 6 <-- insert event , update to 5, update to 6
orange 1

Whenever is there change in table state change, you stream the output, table change as stream 

(apple, 2)
(apple, 5)
(orange, 1)
(apple, 6)
```










```
