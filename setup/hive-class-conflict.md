ProtoBuf class conflict error for ORC

APP_LOG="$HOME/hadoop-data/yarn/log/application_1787067843523_0005"

grep -RniE -B 15 -A 50 \
  'exception|caused by|error|failed|fatal|exit code|exitcode|killed' \
  "$APP_LOG"

grep -RniE -B 15 -A 50 \
  'exception|caused by|error|failed|fatal|exit code|exitcode|killed' \
  "$APP_LOG" \
  > /tmp/application-0005-errors.txt

less /tmp/application-0005-errors.txt


The actual error 

java.lang.NoSuchMethodError:
com.google.protobuf.Internal.checkNotNull(java.lang.Object)



It appears that hive ORC load ProtoBuf library from hadoop isntead of supplied hive configuration.

in beeline

```
SET mapreduce.job.user.classpath.first=true;
```

copy below to hive-site.xml

```
<property>
    <name>mapreduce.job.user.classpath.first</name>
    <value>true</value>
    <description>
        Load Hive and ORC dependencies before Hadoop dependencies in MapReduce containers
    </description>
</property>
```
