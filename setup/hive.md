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

