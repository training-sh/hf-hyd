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


```
import httpx
import google.auth

from google import genai
from google.genai import types


PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
MODEL_ID = "gemini-2.5-flash"


def make_client(location=None):
    # Equivalent idea to requests.Session(verify=False)
    httpx_client = httpx.Client(
        verify=False,
        timeout=120.0,
    )

    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=location or LOCATION,
        http_options=types.HttpOptions(
            api_version="v1",
            httpx_client=httpx_client,
        ),
    )


# Check Application Default Credentials
credentials, detected_project = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

print("Credential type:", type(credentials).__name__)
print("ADC project:", detected_project)


# Create Vertex AI Gemini client
client = make_client()


response = client.models.generate_content(
    model=MODEL_ID,
    contents="Explain generative AI to a Python beginner in three sentences.",
    config=types.GenerateContentConfig(
        max_output_tokens=1000
    ),
)

print(response.text)
print(response.usage_metadata)

```

