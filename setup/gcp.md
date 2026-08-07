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
