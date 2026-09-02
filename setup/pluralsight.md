## Setup don't use until instructed

```
sudo apt update
```

```
sudo apt update
```

```
sudo apt install -y certbot python3-certbot-nginx
```
nginx webserver

```
sudo apt install nginx
```

```
sudo systemctl enable --now nginx
```

check this return full domain name, hostname.domainname.tld, example lab123.example.com

```
hostname -f
```

Obtain ssl certification for subdomain, this helps you access https://lab123.example.com


```
# List current firewall rules and allowed ports
sudo ufw status numbered

# Allow required TCP ports
sudo ufw allow 80/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Verify
sudo ufw status verbose
```

```
sudo certbot --nginx \
  -d "$(hostname -f)" \
  --non-interactive \
  --register-unsafely-without-email \
  --agree-tos \
  --redirect
```

```
/etc/letsencrypt/live/<hostname>/
```

sudo ls -l "/etc/letsencrypt/live/$(hostname -f)/"


fullchain.pem  # Nginx certificate + intermediate chain
privkey.pem    # Private key
cert.pem       # Server certificate
chain.pem      # Intermediate certificates


ssl_certificate     /etc/letsencrypt/live/your-host/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-host/privkey.pem;

check the path

sudo certbot certificates


```
sudo apt install -y python3-venv
```

```
python3 -m venv ~/dataengenv
source ~/dataengenv/bin/activate
```

```
cat <<'EOF' >> ~/.bashrc

# Automatically activate the Data Engineering environment
if [ -f "$HOME/dataengenv/bin/activate" ]; then
    source "$HOME/dataengenv/bin/activate"
fi
EOF

```


```
python -m pip install --upgrade pip
```

```
pip install jupyterlab
```

```
sudo apt install -y apache2-utils
```

```
sudo htpasswd -c /etc/nginx/.htpasswd <<student>>
```

example

sudo htpasswd -c /etc/nginx/.htpasswd joe

```
sudo tee /etc/nginx/snippets/jupyter-proxy.conf >/dev/null <<'EOF'
location = /jupyter {
    return 301 /jupyter/;
}

location /jupyter/ {
    proxy_pass http://127.0.0.1:8888/jupyter/;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;

    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
    proxy_buffering off;
}
EOF
```

```
sudo tee /etc/nginx/snippets/lab-auth.conf >/dev/null <<'EOF'
auth_basic "Restricted Training Lab";
auth_basic_user_file /etc/nginx/.htpasswd;
EOF
```

```
sudo nano /etc/nginx/sites-available/default
```

watch for server block , that has listen 443 ssl , include above file 

```
include /etc/nginx/snippets/lab-auth.conf;
include /etc/nginx/snippets/jupyter-proxy.conf;
```

test your editing skill with below command, -t validate config

```
sudo nginx -t
```

reload nginx

```
sudo systemctl reload nginx
```

enter your password, confirm your password. if you forgot your jupyter password, reset again in same way.

```
jupyter server password
```

for reference

```
jupyter lab \
  --ip=127.0.0.1 \
  --port=8888 \
  --no-browser \
  --ServerApp.base_url=/jupyter/ \
  --ServerApp.allow_remote_access=True
```

hashed password

```
cat ~/.jupyter/jupyter_server_config.json
```
 

```
touch ~/.aws-jupyter.env

nano ~/.aws-jupyter.env

```

paste below, replace your password from aws/ps

```
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
```

this is to refresh the key and password

```
tee ~/awsrefresh >/dev/null <<'EOF'
read -rp "AWS Access Key ID: " key
read -rsp "AWS Secret Access Key: " secret
echo

printf 'AWS_ACCESS_KEY_ID=%s\nAWS_SECRET_ACCESS_KEY=%s\n' \
  "$key" "$secret" > "$HOME/.aws-jupyter.env"

chmod 600 "$HOME/.aws-jupyter.env"
sudo systemctl restart jupyter

echo "AWS credentials updated and Jupyter restarted."
unset key secret
EOF
```

create jupter as linux service

sudo tee /etc/systemd/system/jupyter.service >/dev/null <<'EOF'
[Unit]
Description=JupyterLab
After=network.target nginx.service

[Service]
Type=simple
User=cloud_user
Group=cloud_user
WorkingDirectory=/home/cloud_user

EnvironmentFile=/home/cloud_user/.aws-jupyter.env

Environment="HOME=/home/cloud_user"

Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"

Environment="HADOOP_HOME=/opt/hadoop"
Environment="HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop"
Environment="YARN_CONF_DIR=/opt/hadoop/etc/hadoop"

Environment="SPARK_HOME=/opt/spark"

Environment="PYSPARK_PYTHON=/home/cloud_user/dataengenv/bin/python"
Environment="PYSPARK_DRIVER_PYTHON=/home/cloud_user/dataengenv/bin/python"

Environment="PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip"

Environment="PATH=/home/cloud_user/dataengenv/bin:/opt/spark/bin:/opt/spark/sbin:/opt/hadoop/bin:/opt/hadoop/sbin:/usr/local/bin:/usr/bin:/bin"

Environment="AWS_SHARED_CREDENTIALS_FILE=/home/cloud_user/.aws/credentials"
Environment="AWS_CONFIG_FILE=/home/cloud_user/.aws/config"

ExecStart=/home/cloud_user/dataengenv/bin/jupyter lab \
  --no-browser \
  --ip=127.0.0.1 \
  --port=8888 \
  --ServerApp.base_url=/jupyter/ \
  --ServerApp.allow_remote_access=True

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart jupyter
sudo systemctl status jupyter --no-pager


```
sudo systemctl daemon-reload

sudo systemctl enable --now jupyter
```

```
sudo systemctl status jupyter --no-pager
sudo journalctl -u jupyter -n 50 --no-pager
```

```
sudo ss -lntp | grep ':8888'
```

## Spark History Server for EMR cluster for PS workaround

```
sudo tee /etc/nginx/snippets/emr-proxies.conf >/dev/null <<'EOF'
# ==========================================================
# EMR services through local SSH tunnels
# ==========================================================

# YARN ResourceManager
# Local tunnel: 127.0.0.1:18088 -> EMR Primary:8088
location = /yarn {
    return 301 /yarn/;
}

location /yarn/ {
    proxy_pass http://127.0.0.1:18088/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_redirect ~^(/.*)$ /yarn$1;

    proxy_connect_timeout 10s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}


# HDFS NameNode
# Local tunnel: 127.0.0.1:19870 -> EMR Primary:9870
location = /hdfs {
    return 301 /hdfs/;
}

location /hdfs/ {
    proxy_pass http://127.0.0.1:19870/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_redirect ~^(/.*)$ /hdfs$1;

    proxy_connect_timeout 10s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}


# Spark History Server
# Local tunnel: 127.0.0.1:18080 -> EMR Primary:18080
location = /spark-history {
    return 301 /spark-history/;
}

location /spark-history/ {
    proxy_pass http://127.0.0.1:18080/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_redirect ~^(/.*)$ /spark-history$1;

    proxy_connect_timeout 10s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}


# MapReduce JobHistory Server
# Local tunnel: 127.0.0.1:19888 -> EMR Primary:19888
location = /job-history {
    return 301 /job-history/;
}

location /job-history/ {
    proxy_pass http://127.0.0.1:19888/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_redirect ~^(/.*)$ /job-history$1;

    proxy_connect_timeout 10s;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}


# Apache Livy REST API
# Local tunnel: 127.0.0.1:18998 -> EMR Primary:8998
location = /livy {
    return 301 /livy/;
}

location /livy/ {
    proxy_pass http://127.0.0.1:18998/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 10s;
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;

    # Important for long-running Livy requests and log streaming
    proxy_buffering off;
    proxy_request_buffering off;
}
EOF
```

## include emr proxies

```
sudo nano /etc/nginx/sites-available/default
```

```
include /etc/nginx/snippets/emr-proxies.conf;
```



## DONT USE this until instructed, Spark history server if the cluster runs in the VM

```
sudo tee /etc/nginx/snippets/spark-history.conf >/dev/null <<'EOF'
location = /spark-history {
    return 301 /spark-history/;
}

location /spark-history/ {
    proxy_pass http://127.0.0.1:18080/;
    proxy_http_version 1.1;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Spark uses this when generating asset and application links
    proxy_set_header X-Forwarded-Context /spark-history;

    proxy_redirect off;
}
EOF
```


```
sudo nano /etc/nginx/sites-available/default
```

paste it with other jupyter, default auth 

```
include /etc/nginx/snippets/spark-history.conf;
```




# Guacamole, skip for HF training, until needed


```
sudo tee /etc/nginx/snippets/guacamole-proxy.conf > /dev/null <<'EOF'
location = /guacamole {
    return 301 /guacamole/;
}

location /guacamole/ {
    proxy_pass http://127.0.0.1:8080/guacamole/;

    proxy_http_version 1.1;
    proxy_buffering off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
EOF
```



```
sudo nano /etc/nginx/sites-available/default
```

```
  include /etc/nginx/snippets/guacamole-proxy.conf;
```

```
sudo nginx -t
```

```
sudo systemctl reload nginx
```

```
source ~/awsrefresh
```

```
sudo systemctl restart jupyter
```
