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
