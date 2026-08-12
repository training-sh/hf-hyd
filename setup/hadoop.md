#### Java setup

```
sudo apt update
```


```
sudo apt install -y openjdk-11-jdk
```

```
/usr/lib/jvm/java-11-openjdk-amd64/bin/java -version
```



```
sudo apt install -y \
  openjdk-11-jdk \
  openssh-server \
  wget \
  curl \
  rsync
```

Ensure java 17

```
java -version
```

```
javac -version
```
check the path where java available
```
dirname "$(dirname "$(readlink -f "$(which java)")")"
```

```
sudo cat /etc/environment
```

if below files, you will brick your linux, no warranty, no support

```
sudo tee -a /etc/environment > /dev/null <<'EOF'
JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
HADOOP_HOME="/opt/hadoop"
HADOOP_CONF_DIR="/opt/hadoop/etc/hadoop"
EOF
```

check again , if we could see java env added, 



```
sudo cat /etc/environment
```

.bashrc support

```
tee -a "$HOME/.bashrc" > /dev/null <<'EOF'

# Hadoop environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"
EOF
```

```
source "$HOME/.bashrc"
```

```
cd /tmp

wget -O hadoop-3.3.6.tar.gz \
  https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
```

```
sudo tar -xzf /tmp/hadoop-3.3.6.tar.gz -C /opt

sudo mv /opt/hadoop-3.3.6 /opt/hadoop

sudo chown -R "$USER:$(id -gn)" /opt/hadoop
```

```
hadoop version
```

```
mkdir -p "$HOME/hadoop-data/tmp"
mkdir -p "$HOME/hadoop-data/namenode"
mkdir -p "$HOME/hadoop-data/datanode"
mkdir -p "$HOME/hadoop-data/yarn/local"
mkdir -p "$HOME/hadoop-data/yarn/log"
mkdir -p "$HOME/hadoop-logs"

mkdir -p "$HOME/hadoop-data/namesecondary"

```

available storage

```
df -h "$HOME"
free -h
```

core-site.xml


```
tee "$HADOOP_CONF_DIR/core-site.xml" > /dev/null <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>

    <property>
        <name>hadoop.tmp.dir</name>
        <value>${user.home}/hadoop-data/tmp</value>
    </property>

    <property>
        <name>io.file.buffer.size</name>
        <value>65536</value>
    </property>

</configuration>
EOF
```

hdfs-site.xml

```
tee "$HADOOP_CONF_DIR/hdfs-site.xml" > /dev/null <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>

    <property>
        <name>dfs.blocksize</name>
        <value>67108864</value>
        <description>64 MB blocks for a small training cluster</description>
    </property>

    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file://${user.home}/hadoop-data/namenode</value>
    </property>

    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file://${user.home}/hadoop-data/datanode</value>
    </property>

    <property>
        <name>dfs.namenode.checkpoint.dir</name>
        <value>file://${user.home}/hadoop-data/namesecondary</value>
    </property>

    <property>
        <name>dfs.permissions.enabled</name>
        <value>true</value>
    </property>

</configuration>
EOF
```

mapred-site.xml

```
tee "$HADOOP_CONF_DIR/mapred-site.xml" > /dev/null <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>

    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>

    <property>
        <name>mapreduce.map.memory.mb</name>
        <value>1024</value>
    </property>

    <property>
        <name>mapreduce.map.java.opts</name>
        <value>-Xmx768m</value>
    </property>

    <property>
        <name>mapreduce.reduce.memory.mb</name>
        <value>1536</value>
    </property>

    <property>
        <name>mapreduce.reduce.java.opts</name>
        <value>-Xmx1024m</value>
    </property>

    <property>
        <name>yarn.app.mapreduce.am.resource.mb</name>
        <value>768</value>
    </property>

    <property>
        <name>yarn.app.mapreduce.am.command-opts</name>
        <value>-Xmx512m</value>
    </property>

    <property>
        <name>mapreduce.jobhistory.address</name>
        <value>localhost:10020</value>
    </property>

    <property>
        <name>mapreduce.jobhistory.webapp.address</name>
        <value>localhost:19888</value>
    </property>

</configuration>
EOF
```

yarn-site.xml

```
tee "$HADOOP_CONF_DIR/yarn-site.xml" > /dev/null <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>localhost</value>
    </property>

    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>

    <property>
        <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>

    <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>8192</value>
        <description>Maximum total memory available to YARN containers</description>
    </property>

    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>512</value>
    </property>

    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>8192</value>
    </property>

    <property>
        <name>yarn.nodemanager.resource.cpu-vcores</name>
        <value>4</value>
    </property>

    <property>
        <name>yarn.scheduler.minimum-allocation-vcores</name>
        <value>1</value>
    </property>

    <property>
        <name>yarn.scheduler.maximum-allocation-vcores</name>
        <value>4</value>
    </property>

    <property>
        <name>yarn.nodemanager.local-dirs</name>
        <value>${user.home}/hadoop-data/yarn/local</value>
    </property>

    <property>
        <name>yarn.nodemanager.log-dirs</name>
        <value>${user.home}/hadoop-data/yarn/log</value>
    </property>

    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
        <description>Avoid unreliable virtual-memory checks under WSL</description>
    </property>

    <property>
        <name>yarn.nodemanager.pmem-check-enabled</name>
        <value>true</value>
    </property>

    <property>
        <name>yarn.log-aggregation-enable</name>
        <value>false</value>
        <description>Disabled to avoid accumulating training logs in HDFS</description>
    </property>

    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME,CLASSPATH_PREPEND_DISTCACHE</value>
    </property>

</configuration>
EOF
```


```

tee -a "$HADOOP_CONF_DIR/hadoop-env.sh" > /dev/null <<'EOF'

# Training-cluster environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_LOG_DIR="${HOME}/hadoop-logs"

# Small single-node cluster heap limits
export HDFS_NAMENODE_OPTS="-Xmx512m ${HDFS_NAMENODE_OPTS}"
export HDFS_DATANODE_OPTS="-Xmx512m ${HDFS_DATANODE_OPTS}"
export HDFS_SECONDARYNAMENODE_OPTS="-Xmx256m ${HDFS_SECONDARYNAMENODE_OPTS}"
EOF
```

```
tee -a "$HADOOP_CONF_DIR/yarn-env.sh" > /dev/null <<'EOF'

# Training-cluster environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export YARN_RESOURCEMANAGER_HEAPSIZE=512
export YARN_NODEMANAGER_HEAPSIZE=512
EOF
```

job history

```
tee -a "$HADOOP_CONF_DIR/mapred-env.sh" > /dev/null <<'EOF'

# Training-cluster environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_JOB_HISTORYSERVER_HEAPSIZE=256
EOF
```

configure workers list

```
printf '%s\n' localhost > "$HADOOP_CONF_DIR/workers"
```

check 

```
cat "$HADOOP_CONF_DIR/workers"
```

XML validation

```
sudo apt install -y libxml2-utils
```

Copy whole thing, ensure all four xml are good, no syntactical error, here we validate xml format, not hadoop conf right or wrong.

```
for file in core-site.xml hdfs-site.xml mapred-site.xml yarn-site.xml
do
    echo "Checking $file"
    xmllint --noout "$HADOOP_CONF_DIR/$file"
done
```

Resolved home directory, especially to validate ${user.home} worked or not,
it must show your home directory

Confirm resolved directories

Hadoop can show the resolved values:

```
hdfs getconf -confKey fs.defaultFS
hdfs getconf -confKey hadoop.tmp.dir
hdfs getconf -confKey dfs.namenode.name.dir
hdfs getconf -confKey dfs.datanode.data.dir
```

CRITICAL PART

Verify passwordless SSH

```
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

ssh-keyscan -H localhost >> "$HOME/.ssh/known_hosts"
chmod 600 "$HOME/.ssh/known_hosts"
```

```
ssh -o BatchMode=yes localhost 'echo "SSH working as $(whoami)"'
```

if above failed, you need to configure ssh key

```
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
    ssh-keygen -t ed25519 -N "" -f "$HOME/.ssh/id_ed25519"
fi

touch "$HOME/.ssh/authorized_keys"

grep -qxF "$(cat "$HOME/.ssh/id_ed25519.pub")" \
    "$HOME/.ssh/authorized_keys" ||
    cat "$HOME/.ssh/id_ed25519.pub" >> "$HOME/.ssh/authorized_keys"

chmod 600 "$HOME/.ssh/authorized_keys"
```

check again, you must see echo msg printed

```
ssh -o BatchMode=yes localhost 'echo "SSH working as $(whoami)"'
```

Hadoop Formatting

Below command is to test, if hadoop has some files, if no shows shown, means , we need to format hdfs freshly

```
find "$HOME/hadoop-data/namenode" -maxdepth 2 -type f
```

format hdfs now. it is like formatting your pen drive, harddisk etc but limited to hadoop. 

```
hdfs namenode -format hadoop-training
```

check again, if any files found, we expect few defaults added by hadoop format command

```
find "$HOME/hadoop-data/namenode" -maxdepth 2 -type f
```

Now real fun start, did we really configure correctly or not

Start HDFS

```
start-dfs.sh
```

check namenode, datanode, secondary data node, also adding your host into known host list

to check these services alive or dead,

jps command print running java processes

```
jps
```

must print 

xyz SecondaryNameNode

xyz DataNode

xyz NameNode

xyz is process id

HDFS Health check

```
hdfs dfsadmin -report
```

while it prints more details, validate it has a line

Live datanodes (1):


Now you are reaching The Shawshank Redemption  climax, whether Andy escaped jail, living happily on sea shore with his dream boat else ??

create directories in hdfs

```
hdfs dfs -mkdir -p "/user/$USER"
hdfs dfs -chown "$USER:$(id -gn)" "/user/$USER"
```

```
hdfs dfs -ls /user
```

List them

Now real test start, can we upload file, creating directories did not use datanodes, it uses only namenode.

Let us upload a file into hdfs

```
mkdir -p "$HOME/hadoop-lab/input"
```

create a localfile to upload into cloud files

```
tee "$HOME/hadoop-lab/input/file1.txt" > /dev/null <<'EOF'
hadoop stores large data
hadoop uses hdfs
mapreduce processes data
EOF
```

yet another local file to test your patience

```
tee "$HOME/hadoop-lab/input/file2.txt" > /dev/null <<'EOF'
hdfs stores blocks
yarn manages resources
mapreduce runs on yarn
EOF
```

yet another hdfs directory

```
hdfs dfs -mkdir -p input
```

upload files.. pray favorite gods, most hdfs setup fails here due to datanode, hdfs formatting

```
hdfs dfs -put -f "$HOME/hadoop-lab/input/"*.txt input/
```

sure, done, take deep breath!!, check if upload successful yet

```
hdfs dfs -ls input
```

```
hdfs dfs -cat 'input/*.txt'
```

does it print content?, celebrate!!, have small talk, non technical.. you earned 10 mins break

Still not yet done fully, we have to check Map Reduce/YARN

## Start YARN


```
start-yarn.sh
```

must start resourcemanager, nodemanagers

```
jps
```



# Utilities, logs

```
find "$HOME/hadoop-logs" -maxdepth 1 -type f \
  -printf '%T@ %p\n' |
  sort -nr |
  head -10 |
  cut -d' ' -f2-
```

```
grep -RniE \
  'exception|error|failed|inaccessible|unsupported|could not' \
  "$HOME/hadoop-logs" |
  tail -80
```

end of daemon logs, if any error in resource or nodemanager, if they didn't start these logs unlikely present or may have last known errors

```
for file in "$HOME"/hadoop-logs/*resourcemanager* \
            "$HOME"/hadoop-logs/*nodemanager*
do
    [ -f "$file" ] || continue
    echo "===== $file ====="
    tail -80 "$file"
done
```












