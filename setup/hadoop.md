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




