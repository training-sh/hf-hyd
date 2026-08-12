

  GNU nano 6.2                                            /etc/nginx/snippets/hadoop-uis.conf 


```
# Paths without trailing slash
location = /hdfs {
    return 302 /hdfs/;
}

location = /yarn {
    return 302 /yarn/;
}

location = /history {
    return 302 /history/;
}


# HDFS NameNode UI
location /hdfs/ {
    proxy_pass http://127.0.0.1:9870/;
    proxy_http_version 1.1;

    proxy_set_header Host 127.0.0.1:9870;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Accept-Encoding "";

    proxy_redirect ~^http://[^/]+:9870/(.*)$ /hdfs/$1;
    proxy_redirect ~^/(.*)$ /hdfs/$1;

    sub_filter_once off;
    sub_filter_types text/css application/javascript application/json;

    sub_filter 'href="/' 'href="/hdfs/';
    sub_filter "href='/" "href='/hdfs/";
    sub_filter 'src="/' 'src="/hdfs/';
    sub_filter "src='/" "src='/hdfs/";
    sub_filter 'action="/' 'action="/hdfs/';
}


# YARN ResourceManager UI
location /yarn/ {
    proxy_pass http://127.0.0.1:8088/;
    proxy_http_version 1.1;

    proxy_set_header Host 127.0.0.1:8088;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Accept-Encoding "";

    proxy_redirect ~^http://[^/]+:8088/(.*)$ /yarn/$1;
    proxy_redirect ~^/(.*)$ /yarn/$1;

    sub_filter_once off;
    sub_filter_types text/css application/javascript application/json;

    sub_filter 'href="/' 'href="/yarn/';
    sub_filter "href='/" "href='/yarn/";
    sub_filter 'src="/' 'src="/yarn/';
    sub_filter "src='/" "src='/yarn/";
    sub_filter 'action="/' 'action="/yarn/';

    # YARN paths generated inside JavaScript
    sub_filter '"/cluster' '"/yarn/cluster';
    sub_filter "'/cluster" "'/yarn/cluster";
    sub_filter '"/ws/' '"/yarn/ws/';
    sub_filter "'/ws/" "'/yarn/ws/";
    sub_filter '"/proxy/' '"/yarn/proxy/';
    sub_filter "'/proxy/" "'/yarn/proxy/";
}


# Compatibility for YARN links that escape the /yarn prefix
location = /cluster {
    return 302 /yarn/cluster;
}

location /cluster/ {
    rewrite ^/cluster/(.*)$ /yarn/cluster/$1 redirect;
}

location /proxy/ {
    rewrite ^/proxy/(.*)$ /yarn/proxy/$1 redirect;
}


# MapReduce JobHistory UI
location /history/ {
    proxy_pass http://127.0.0.1:19888/;
    proxy_http_version 1.1;

    proxy_set_header Host 127.0.0.1:19888;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Accept-Encoding "";

    proxy_redirect ~^http://[^/]+:19888/(.*)$ /history/$1;
    proxy_redirect ~^/(.*)$ /history/$1;

    sub_filter_once off;
    sub_filter_types text/css application/javascript application/json;

    sub_filter 'href="/' 'href="/history/';
    sub_filter "href='/" "href='/history/";
    sub_filter 'src="/' 'src="/history/';
    sub_filter "src='/" "src='/history/";
    sub_filter 'action="/' 'action="/history/';
}



# NameNode UI uses the absolute /jmx endpoint
location = /jmx {
    proxy_pass http://127.0.0.1:9870/jmx$is_args$args;
    proxy_http_version 1.1;

    proxy_set_header Host 127.0.0.1:9870;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}


# HDFS Explorer uses the absolute /webhdfs endpoint
location /webhdfs/ {
    proxy_pass http://127.0.0.1:9870/webhdfs/;
    proxy_http_version 1.1;

    proxy_set_header Host 127.0.0.1:9870;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Rewrite NameNode redirects back through Nginx
    proxy_redirect ~^http://[^/]+:9870/(.*)$ /$1;
}
```


