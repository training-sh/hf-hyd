# Apache Livy

```
sudo apt-get update
```

```
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  wget \
  unzip \
  gcc \
  python3-dev \
  libkrb5-dev \
  krb5-config
```

```
cd /tmp

wget -O apache-livy-0.9.0-incubating_2.12-bin.zip \
  https://downloads.apache.org/incubator/livy/0.9.0-incubating/apache-livy-0.9.0-incubating_2.12-bin.zip
```

```
sudo unzip /tmp/apache-livy-0.9.0-incubating_2.12-bin.zip -d /opt

sudo mv \
  /opt/apache-livy-0.9.0-incubating_2.12-bin \
  /opt/livy
```

Verify installation

```
ls -ld /opt/livy
ls -l /opt/livy/bin/livy-server
```

```
  tee -a "$HOME/.bashrc" >/dev/null <<'EOF'

# --- Apache Livy configuration ---
export LIVY_HOME=/opt/livy
export PATH="$LIVY_HOME/bin:$PATH"
EOF
```

```
source "$HOME/.bashrc"
```

```
cp /opt/livy/conf/livy.conf.template \
   /opt/livy/conf/livy.conf
```

```
tee -a /opt/livy/conf/livy.conf >/dev/null <<'EOF'

# --- Local Spark through Livy ---
livy.server.host = 127.0.0.1
livy.server.port = 8998
livy.spark.master = local[*]
livy.impersonation.enabled = false
EOF
```

```
tee /opt/livy/conf/livy-env.sh >/dev/null <<'EOF'
export SPARK_HOME=/opt/spark
export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

export PYSPARK_PYTHON="$HOME/dataengenv/bin/python"
export PYSPARK_DRIVER_PYTHON="$HOME/dataengenv/bin/python"

export LIVY_SERVER_JAVA_OPTS="-Xms256m -Xmx512m"
EOF

```

```
chmod +x /opt/livy/conf/livy-env.sh
```

```
if [ -f /opt/livy/conf/log4j.properties.template ]; then
  cp /opt/livy/conf/log4j.properties.template \
     /opt/livy/conf/log4j.properties
elif [ -f /opt/livy/conf/log4j2.properties.template ]; then
  cp /opt/livy/conf/log4j2.properties.template \
     /opt/livy/conf/log4j2.properties
fi
```

```

livy-server start
```
status of livy server

```
livy-server status

ps -ef | grep '[o]rg.apache.livy.server.LivyServer'

ss -lntp | grep 8998
```

```
curl -v http://127.0.0.1:8998/sessions
```

if livy failed,
```

tail -n 150 /opt/livy/logs/livy-"$USER"-server.out
```

Also check for an out-of-memory kill:

```
sudo dmesg --ctime |
grep -Ei 'out of memory|oom|killed process' |
tail -n 20
```

