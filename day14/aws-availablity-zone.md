```
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
-H "X-aws-ec2-metadata-token-ttl-seconds:21600")

echo "Region: $(curl -s -H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/placement/region)"

echo "AZ: $(curl -s -H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/placement/availability-zone)"

echo "AZ ID: $(curl -s -H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/placement/availability-zone-id)"

echo "Type: $(curl -s -H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/instance-type)"

```


```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```

```
df -h
```

```
sudo fdisk -l
```

```
sudo parted -l
```

EBS volume

```
lsblk -o NAME,MODEL,SERIAL
```

```
TOKEN=$(curl -s -X PUT \
"http://169.254.169.254/latest/api/token" \
-H "X-aws-ec2-metadata-token-ttl-seconds:21600")
```

```
curl -s \
-H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```


```
TOKEN=$(curl -s -X PUT \
"http://169.254.169.254/latest/api/token" \
-H "X-aws-ec2-metadata-token-ttl-seconds:21600")

curl -H "X-aws-ec2-metadata-token:$TOKEN" \
http://169.254.169.254/latest/meta-data/block-device-mapping/
```

```
cat /sys/block/nvme0n1/size
```

```
blockdev --getsize64 /dev/nvme0n1
```


```

#!/bin/bash
set -e

echo "==> Removing old Docker packages..."
sudo apt remove -y docker docker-engine docker.io containerd runc || true

echo "==> Installing prerequisites..."
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

echo "==> Adding Docker GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "==> Adding Docker repository..."
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "==> Installing Docker..."
sudo apt update
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo "==> Enabling Docker..."
sudo systemctl enable docker
sudo systemctl restart docker

echo "==> Adding current user to docker group..."
sudo usermod -aG docker $USER

echo
echo "==============================="
echo "Docker Version:"
docker --version || true
echo
echo "Docker Compose Version:"
docker compose version || true
echo
echo "Docker Service:"
sudo systemctl --no-pager --full status docker | head -15
echo "==============================="
echo
echo "Run the following command or log out and back in:"
echo "newgrp docker"
echo
echo "Test with:"
echo "docker run hello-world"

```
