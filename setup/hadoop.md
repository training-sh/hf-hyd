#### Java setup

```
sudo apt update
```

```
sudo apt install -y \
  openjdk-17-jdk \
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
JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
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
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
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



