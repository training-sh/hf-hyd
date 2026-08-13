Hive setup for wsl/ubuntu linux for single node, testing purpose

### do not follow, instructions is in progress

```
wsl
```

```
cd /tmp
```

```
wget -O apache-hive-4.0.1-bin.tar.gz \
  https://archive.apache.org/dist/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz \
  --no-check-certificate
```

```
sudo tar -xzf /tmp/apache-hive-4.0.1-bin.tar.gz -C /opt
```

```
sudo mv /opt/apache-hive-4.0.1-bin /opt/hive
```

we will run hive on logged in user credentials, not as backend. this is not a good practice.

```
sudo chown -R "$USER:$(id -gn)" /opt/hive
```

check ownership

```
ls -ld /opt/hive
```

```
tee -a "$HOME/.bashrc" > /dev/null <<'EOF'

# Apache Hive environment
export HIVE_HOME=/opt/hive
export HIVE_CONF_DIR="$HIVE_HOME/conf"
export PATH="$PATH:$HIVE_HOME/bin"
EOF
```

```
source "$HOME/.bashrc"
```
validate all the available templates, templates are config files examples.

```
ls "$HIVE_CONF_DIR" | sort
```

we clone or create existing template or create $HIVE_CONF_DIR/hive-env.sh

```
if [ -f "$HIVE_CONF_DIR/hive-env.sh.template" ]; then
    cp "$HIVE_CONF_DIR/hive-env.sh.template" \
       "$HIVE_CONF_DIR/hive-env.sh"
else
    touch "$HIVE_CONF_DIR/hive-env.sh"
fi
```

append JAVA, hadoop, hadoop, hive env into hive-env.sh file

```
tee -a "$HIVE_CONF_DIR/hive-env.sh" > /dev/null <<'EOF'

# Hadoop training-lab environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop

# Hive environment
export HIVE_HOME=/opt/hive
export HIVE_CONF_DIR=/opt/hive/conf
export HIVE_LOG_DIR="${HOME}/hive-logs"

# Heap for small WSL training environment
export HADOOP_HEAPSIZE=1024
EOF
```


```
mkdir -p "$HOME/hive-logs"
mkdir -p "$HOME/hive-data/scratch"
mkdir -p "$HOME/hive-data/resources"
```

check hive version , should be 4.0.1

```
hive --version
```

beeline version same as hive version

```
beeline --version
```

```
mysql -u root -p
```

copy paste one after another

```
CREATE DATABASE IF NOT EXISTS hive_metastore;

CREATE USER IF NOT EXISTS 'hive'@'localhost'
IDENTIFIED BY 'HiveLab@123';

ALTER USER 'hive'@'localhost'
IDENTIFIED BY 'HiveLab@123';

GRANT ALL PRIVILEGES
ON hive_metastore.*
TO 'hive'@'localhost';

FLUSH PRIVILEGES;

SHOW DATABASES LIKE 'hive_metastore';

SELECT user, host, plugin
FROM mysql.user
WHERE user = 'hive';

SHOW GRANTS FOR 'hive'@'localhost';

EXIT;
```

test your mysql account for hive working

```
mysql \
  --protocol=TCP \
  -h 127.0.0.1 \
  -P 3306 \
  -u hive \
  -p \
  hive_metastore
```

enter password

ensure database, user..

```
SELECT DATABASE(), CURRENT_USER(), VERSION();
SHOW TABLES;
EXIT;
```

```
wget -O mysql-connector-j-8.4.0.jar \
  https://repo.maven.apache.org/maven2/com/mysql/mysql-connector-j/8.4.0/mysql-connector-j-8.4.0.jar --no-check-certificate
```

copy mysql connector to hive lib directory

```
cp /tmp/mysql-connector-j-8.4.0.jar "$HIVE_HOME/lib/"
```


Setup hive config

```
tee "$HIVE_CONF_DIR/hive-site.xml" > /dev/null <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<configuration>

    <!-- ====================================================== -->
    <!-- MySQL external metastore                               -->
    <!-- Derby embedded metastore is deliberately not used      -->
    <!-- ====================================================== -->

    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:mysql://127.0.0.1:3306/hive_metastore?useSSL=false&amp;allowPublicKeyRetrieval=true&amp;serverTimezone=UTC</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>com.mysql.cj.jdbc.Driver</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionUserName</name>
        <value>hive</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionPassword</name>
        <value>HiveLab@123</value>
    </property>

    <property>
        <name>datanucleus.schema.autoCreateAll</name>
        <value>false</value>
    </property>

    <property>
        <name>hive.metastore.schema.verification</name>
        <value>true</value>
    </property>

    <!-- ====================================================== -->
    <!-- Standalone Hive Metastore service                      -->
    <!-- ====================================================== -->

    <property>
        <name>hive.metastore.uris</name>
        <value>thrift://localhost:9083</value>
    </property>

    <!-- ====================================================== -->
    <!-- HDFS warehouse and scratch directories                 -->
    <!-- ====================================================== -->

    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>

    <property>
        <name>hive.metastore.warehouse.external.dir</name>
        <value>/user/hive/external</value>
    </property>

    <property>
        <name>hive.exec.scratchdir</name>
        <value>/tmp/hive</value>
    </property>

    <property>
        <name>hive.exec.local.scratchdir</name>
        <value>${system:user.home}/hive-data/scratch</value>
    </property>

    <property>
        <name>hive.downloaded.resources.dir</name>
        <value>${system:user.home}/hive-data/resources</value>
    </property>

    <!-- ====================================================== -->
    <!-- MapReduce execution through YARN                       -->
    <!-- ====================================================== -->

    <property>
        <name>hive.execution.engine</name>
        <value>mr</value>
    </property>

    <property>
        <name>hive.fetch.task.conversion</name>
        <value>none</value>
        <description>
            Make query execution visible through MapReduce during training
        </description>
    </property>

    <!-- ====================================================== -->
    <!-- HiveServer2                                            -->
    <!-- ====================================================== -->

    <property>
        <name>hive.server2.thrift.bind.host</name>
        <value>localhost</value>
    </property>

    <property>
        <name>hive.server2.thrift.port</name>
        <value>10000</value>
    </property>

    <property>
        <name>hive.server2.webui.host</name>
        <value>localhost</value>
    </property>

    <property>
        <name>hive.server2.webui.port</name>
        <value>10002</value>
    </property>

    <property>
        <name>hive.server2.authentication</name>
        <value>NONE</value>
    </property>

    <property>
        <name>hive.server2.enable.doAs</name>
        <value>false</value>
        <description>
            Suitable for this single-user WSL training environment
        </description>
    </property>

</configuration>
EOF
```

```
cat $HIVE_CONF_DIR/hive-site.xml
```

