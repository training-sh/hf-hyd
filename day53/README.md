## for update

```
sudo apt-get \
  -o Acquire::https::Verify-Peer=false \
  -o Acquire::https::Verify-Host=false \
  update
```


## Fix for apt install

```
sudo apt-get \
  -o Acquire::https::Verify-Peer=false \
  -o Acquire::https::Verify-Host=false \
  install google-cloud-cli
```

## ssl skip

not sure

```
gcloud config set auth/disable_ssl_validation true
```
