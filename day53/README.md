## Fix for apt install

```
sudo apt-get \
  -o Acquire::https::Verify-Peer=false \
  -o Acquire::https::Verify-Host=false \
  install google-cloud-cli
```
