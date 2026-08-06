
```
sudo apt update
sudo apt upgrade -y

sudo apt install xfce4 xfce4-goodies xrdp xorgxrdp dbus-x11 -y
```


```
printf '%s\n' 'xfce4-session' > ~/.xsession
chmod 644 ~/.xsession
```

```
sudo adduser xrdp ssl-cert
```

```
sudo systemctl enable --now xrdp
sudo systemctl restart xrdp
```

```
sudo systemctl status xrdp --no-pager
sudo ss -lntp | grep 3389
```

# Do not perform this step

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH — add this before enabling UFW
sudo ufw limit 22/tcp comment 'SSH'

# Web services
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# XRDP
sudo ufw allow 3389/tcp comment 'XRDP'

#firewall webconsoel as per pluralsight

sudo ufw allow 31297/tcp comment 'fwwebc'


sudo ufw delete allow 3389/tcp
sudo ufw delete allow 22/tcp


sudo ufw allow from xyz.0.113.yy to any port 3389 proto tcp comment 'XRDP my pg IP'




# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status numbered
sudo ufw status verbose

