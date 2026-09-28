```
# Google Cloud CLI Setup on Ubuntu

This guide sets up Google Cloud CLI (`gcloud`) on Ubuntu and configures authentication for both CLI commands and Python applications.

---

## 1. Check Python

Python is already installed, but verify it:

```bash
python --version
```

Also check `pip`:

```bash
python -m pip --version
```

---

## 2. Install Google Cloud CLI

Install the required packages:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates gnupg curl
```

Add the Google Cloud repository:

```bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
| sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
```

Import Google's repository signing key:

```bash
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
| sudo gpg --dearmor \
-o /usr/share/keyrings/cloud.google.gpg
```

Install Google Cloud CLI:

```bash
sudo apt-get update
sudo apt-get install -y google-cloud-cli
```

Verify:

```bash
gcloud --version
```

---

# 3. Login to Google Cloud

Run:

```bash
gcloud auth login
```

If the Ubuntu machine does not have a usable browser, use:

```bash
gcloud auth login --no-launch-browser
```

Follow the authentication instructions displayed by `gcloud`.

Check the authenticated accounts:

```bash
gcloud auth list
```

---

# 4. AWS Profile Equivalent in GCP

AWS CLI commonly uses named profiles:

```bash
aws configure --profile training
```

and then:

```bash
aws s3 ls --profile training
```

Google Cloud has a similar concept called **gcloud configurations**.

List configurations:

```bash
gcloud config configurations list
```

Create a configuration named `training`:

```bash
gcloud config configurations create training
```

Activate it:

```bash
gcloud config configurations activate training
```

Configure the project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Configure a default region:

```bash
gcloud config set compute/region us-central1
```

Configure a default zone:

```bash
gcloud config set compute/zone us-central1-a
```

Check the configuration:

```bash
gcloud config list
```

---

# 5. Switching Between GCP Configurations

For example, you could maintain:

```text
training
development
production
```

List them:

```bash
gcloud config configurations list
```

Switch to training:

```bash
gcloud config configurations activate training
```

Switch to development:

```bash
gcloud config configurations activate development
```

This is conceptually similar to switching between AWS CLI profiles.

---

# 6. Configure Authentication for Python

`gcloud auth login` authenticates the `gcloud` CLI.

Python Google Cloud libraries normally use **Application Default Credentials (ADC)**.

Configure ADC:

```bash
gcloud auth application-default login
```

On a remote Ubuntu machine without a browser:

```bash
gcloud auth application-default login --no-launch-browser
```

Verify that ADC works:

```bash
gcloud auth application-default print-access-token
```

If authentication is successful, this prints an access token.

---

# 7. Set Environment Variables

Set the GCP project:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
```

For Vertex AI, it is also useful to define a location:

```bash
export GOOGLE_CLOUD_LOCATION="us-central1"
```

Verify:

```bash
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION
```

To make these persistent, add them to `~/.bashrc`:

```bash
echo 'export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"' >> ~/.bashrc
echo 'export GOOGLE_CLOUD_LOCATION="us-central1"' >> ~/.bashrc
```

Reload:

```bash
source ~/.bashrc
```

---

# 8. Install Google Cloud Python Libraries

Prefer using a Python virtual environment:

```bash
python3 -m venv ~/gcpenv
```

Activate it:

```bash
source ~/gcpenv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the Google authentication libraries:

```bash
pip install google-auth google-cloud-core
```

For Vertex AI:

```bash
pip install google-cloud-aiplatform
```

---

# 9. Test Authentication from Python

Create a quick test:

```python
import google.auth

credentials, project_id = google.auth.default()

print("Project ID:", project_id)
print("Credential type:", type(credentials).__name__)
```

Google's Python libraries will automatically search for Application Default Credentials.

---

# 10. Important Difference from AWS

A useful mental mapping is:

| AWS | Google Cloud |
|---|---|
| AWS CLI | `gcloud` CLI |
| `aws configure` | `gcloud init` / `gcloud config` |
| AWS named profile | gcloud named configuration |
| `--profile training` | `gcloud config configurations activate training` |
| `AWS_PROFILE` | Active gcloud configuration |
| Access key / secret key | Google authentication credentials |
| boto3 | Google Cloud Python client libraries |
| `~/.aws/credentials` | ADC / gcloud credential storage |
| `AWS_DEFAULT_REGION` | Service-specific GCP region/location configuration |

---

# 11. Recommended Training Setup

For each student:

```bash
gcloud auth login
gcloud auth application-default login
```

Create a training configuration:

```bash
gcloud config configurations create training
gcloud config configurations activate training
gcloud config set project YOUR_PROJECT_ID
```

Set application environment variables:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

Then verify:

```bash
gcloud auth list
gcloud config list
gcloud auth application-default print-access-token
```

Python applications can now use ADC without embedding passwords, tokens, or credential files in source code.



### just for reference

```
  
  2  PROJECT_ID=$(gcloud config get-value project)
    3  gcloud org-policies describe constraints/gcp.resourceLocations   --project="$PROJECT_ID"   --effective   --format=yaml
    4  gcloud config set dataproc/region us-central1
    5  gcloud config set compute/region us-central1
    6  gcloud config set compute/zone us-central1-a
    7  gcloud dataproc clusters create my-cluster   --region=us-central1   --zone=us-central1-a   --single-node
    8  PROJECT_ID=$(gcloud config get-value project)
    9  gcloud org-policies describe custom.machineTypeWhitelist   --project="$PROJECT_ID"   --effective   --format=yaml
   10  gcloud org-policies describe-custom-constraint   custom.machineTypeWhitelist   --organization=174037535175   --format=yaml
   11  gcloud dataproc clusters create my-cluster   --region=us-central1   --single-node   --master-machine-type=e2-standard-2   --master-boot-disk-size=50GB
   12  gcloud dataproc clusters create my-cluster2   --region=us-central1   --single-node   --master-machine-type=e2-standard-2   --master-boot-disk-size=50GB
   13  history
cloud_user_p_fdd301e4@cloudshell:~ (playground-s-11-fccaad34)$ 

```
