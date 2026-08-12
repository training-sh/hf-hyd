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
sudo certbot --nginx -d "$(hostname -f)"
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
sudo nano /etc/nginx/sites-available/default
```

watch for server block , that has listen 443 ssl , include above file 

```
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
