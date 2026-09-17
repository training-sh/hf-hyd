
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


