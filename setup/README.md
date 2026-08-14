# Security Audit

ensure we don't listen ssh or any application on network port, instead listen only on loopback ip, ie same machine localhost /127.0.0.1

```
wsl
```

```
sudo ss -lntp | grep ':22'
```

if you see entries like 0.0.0.0:22       [::]:22, it means it allow anyone to login into your machine on same network. we don't want that happen.

```
0.0.0.0:22       # all IPv4 interfaces
[::]:22          # all IPv6 interfaces
127.0.0.1:22     # loopback only
```

check sshd itself

```
sudo sshd -T | grep -i '^listenaddress'
```

```
sudo tee /etc/ssh/sshd_config.d/10-loopback-only.conf > /dev/null <<'EOF'
ListenAddress 127.0.0.1
ListenAddress ::1
EOF
```

```
sudo sshd -t
```

```
sudo sshd -T | grep -i '^listenaddress'
```

```
sudo systemctl restart ssh
```

```
ssh -o BatchMode=yes localhost 'echo "SSH working as $(whoami)"'
```

Re-run hdfs commands, get/put, rerun word count again to ensure setup is working


