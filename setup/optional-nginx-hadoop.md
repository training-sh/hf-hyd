nginx mod rewrite for hadoop path, not fully working..

yarn works, hdfs has issue with file download.

## don't follow this
```
sudo tee /etc/nginx/snippets/hadoop-uis.conf > /dev/null <<'EOF'
# Redirect paths without trailing slash
location = /hdfs {
    return 301 /hdfs/;
}

location = /yarn {
    return 301 /yarn/;
}

location = /history {
    return 301 /history/;
}


# HDFS NameNode Web UI
location /hdfs/ {
    include /etc/nginx/snippets/basic-auth.conf;

    proxy_pass http://127.0.0.1:9870/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Disable upstream compression so sub_filter can modify responses
    proxy_set_header Accept-Encoding "";

    proxy_redirect / /hdfs/;

    sub_filter_once off;
    sub_filter_types text/css application/javascript;
    sub_filter 'href="/' 'href="/hdfs/';
    sub_filter 'src="/' 'src="/hdfs/';
    sub_filter 'action="/' 'action="/hdfs/';
}


# YARN ResourceManager Web UI
location /yarn/ {
    include /etc/nginx/snippets/basic-auth.conf;

    proxy_pass http://127.0.0.1:8088/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header Accept-Encoding "";

    proxy_redirect / /yarn/;

    sub_filter_once off;
    sub_filter_types text/css application/javascript;
    sub_filter 'href="/' 'href="/yarn/';
    sub_filter 'src="/' 'src="/yarn/';
    sub_filter 'action="/' 'action="/yarn/';
}


# MapReduce JobHistory Web UI
location /history/ {
    include /etc/nginx/snippets/basic-auth.conf;

    proxy_pass http://127.0.0.1:19888/;
    proxy_http_version 1.1;

    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_set_header Accept-Encoding "";

    proxy_redirect / /history/;

    sub_filter_once off;
    sub_filter_types text/css application/javascript;
    sub_filter 'href="/' 'href="/history/';
    sub_filter 'src="/' 'src="/history/';
    sub_filter 'action="/' 'action="/history/';
}
EOF
```


