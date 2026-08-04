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


```
#!/bin/bash
set -e

echo "==> Updating system..."
sudo apt update
sudo apt upgrade -y

echo "==> Installing XFCE Desktop..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
    xfce4 \
    xfce4-goodies

echo "==> Installing XRDP..."
sudo apt install -y \
    xrdp \
    xorgxrdp

echo "==> Installing useful applications..."
sudo apt install -y \
    firefox \
    dbus-x11 \
    x11-xserver-utils \
    xfce4-terminal \
    thunar \
    gvfs \
    gvfs-backends \
    gvfs-fuse \
    pavucontrol \
    unzip \
    zip \
    curl \
    wget \
    nano \
    git

echo "==> Configure XFCE for XRDP..."
echo "startxfce4" > ~/.xsession
chmod +x ~/.xsession

sudo adduser xrdp ssl-cert || true

echo "==> Enable XRDP..."
sudo systemctl enable xrdp
sudo systemctl restart xrdp

echo "==> Enable Firewall Rule (if UFW exists)..."
if command -v ufw >/dev/null 2>&1; then
    sudo ufw allow 3389/tcp || true
fi

echo
echo "======================================="
echo "Installation Complete"
echo
echo "XRDP Status:"
systemctl --no-pager status xrdp | head -10
echo
echo "Listening Port:"
ss -tlnp | grep 3389 || true
echo
echo "Connect using:"
echo "mstsc.exe"
echo
echo "IP: $(hostname -I | awk '{print $1}')"
echo "Port: 3389"
echo "======================================="
```
