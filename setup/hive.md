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
