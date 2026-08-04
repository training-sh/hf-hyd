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
