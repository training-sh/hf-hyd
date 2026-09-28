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

cli, worked

```
gcloud config set auth/disable_ssl_validation true
```

for python,

```
export PYTHONHTTPSVERIFY=0
```





request, not useful for present scenarios
```
import requests

response = requests.get(
    "https://www.googleapis.com",
    verify=False
)
```

```


openssl x509 -in corporate-ca.crt -noout -subject -issuer

Then create the combined Python bundle:
mkdir -p ~/certs

cat "$(python -m certifi)" corporate-ca.crt \
  > ~/certs/corporate-ca-bundle.pem

Configure Python:
export REQUESTS_CA_BUNDLE="$HOME/certs/corporate-ca-bundle.pem"
export SSL_CERT_FILE="$HOME/certs/corporate-ca-bundle.pem"

Test requests:
python - <<'PY'
import requests

r = requests.get("https://www.googleapis.com")
print(r.status_code)
print("SSL verification succeeded")
PY

If openssl x509 says Unable to load certificate, your .crt is probably DER. Convert it:
openssl x509 \
  -inform DER \
  -in corporate-ca.crt \
  -out corporate-ca.pem

Then use corporate-ca.pem when building the bundle.

```

