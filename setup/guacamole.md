# not needed for participants

# guacamule

```
sudo mkdir -p /opt/guacamole
sudo chown -R "$USER":"$USER" /opt/guacamole
cd /opt/guacamole
```

```
printf '%s' 'YourStrongGuacamolePassword' | md5sum
```


```
nano /opt/guacamole/user-mapping.xml
```

```
<user-mapping>
    <authorize
        username="guacuser"
        password="PASTE_MD5_HASH_HERE"
        encoding="md5">

        <connection name="Ubuntu XRDP">
            <protocol>rdp</protocol>

            <param name="hostname">host.docker.internal</param>
            <param name="port">3389</param>

            <param name="security">any</param>
            <param name="ignore-cert">true</param>

            <param name="color-depth">24</param>
            <param name="resize-method">display-update</param>

            <param name="enable-wallpaper">false</param>
            <param name="enable-theming">false</param>
            <param name="enable-font-smoothing">true</param>
            <param name="enable-full-window-drag">false</param>
        </connection>
    </authorize>
</user-mapping>
```


```
chmod 644 /opt/guacamole/user-mapping.xml
```

```
nano /opt/guacamole/compose.yaml
```

xrdp verification

```
sudo systemctl status xrdp --no-pager
sudo ss -lntp | grep 3389
```

```
cd /opt/guacamole

docker compose pull
docker compose up -d
docker compose ps
```
