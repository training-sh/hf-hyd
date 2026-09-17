
```
wget --no-check-certificate \
  https://archive.apache.org/dist/kafka/3.9.1/kafka_2.13-3.9.1.tgz
```

```
wsl
```

```
cd Downloads
```

```
sudo tar -xzf kafka_2.13-3.9.1.tgz -C /opt
```

```
sudo mv /opt/kafka_2.13-3.9.1 /opt/kafka
```

```
sudo chown -R "$USER:$(id -gn)" /opt/kafka
```


```
tee -a "$HOME/.bashrc" > /dev/null <<'EOF'

# Kafka environment
export KAFKA_HOME=/opt/kafka
export PATH="$PATH:$KAFKA_HOME/bin"
EOF
```

```
cd ~
```

```
source "$HOME/.bashrc" 
```


```
echo "$KAFKA_HOME"
kafka-topics.sh --version
```

