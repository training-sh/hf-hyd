```
docker run -d \
  --name emr-firefox-http \
  -p 127.0.0.1:8880:3000 \
  --shm-size="1gb" \
  --restart unless-stopped \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Asia/Kolkata \
  -e SUBFOLDER=/firefox/ \
  -v /opt/emr-firefox-http/config:/config \
  -v /opt/emr-browser-downloads:/config/Downloads \
  lscr.io/linuxserver/firefox:latest
```

```
sudo nano  /etc/nginx/snippets/firefox-proxy.conf
```

paste below



```
location = /firefox {
    return 301 /firefox/;
}

location /firefox/ {
    proxy_pass http://127.0.0.1:8880/firefox/;

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
    proxy_request_buffering off;

    # Allows file uploads through the streamed-browser interface.
    client_max_body_size 0;
}
```
