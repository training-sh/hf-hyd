
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
