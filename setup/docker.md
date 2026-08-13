# docker

for remote vm

Strictly not for wsl, not for corporate laptop. 

```
sudo apt update
```
```
sudo apt install -y docker.io docker-compose-v2
```
```
sudo systemctl enable --now docker
```
```
sudo usermod -aG docker "$USER"
```

```
newgrp docker
```

```
docker --version
docker compose version
docker run --rm hello-world
```
