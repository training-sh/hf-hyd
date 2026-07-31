```

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

HOST = "0.0.0.0"
PORT = 8443   # Use 443 if running as root

CERT = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
KEY = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"

httpd = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT, keyfile=KEY)

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Listening on https://{HOST}:{PORT}")
httpd.serve_forever()

```



```
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"HTTPS certificate is working\n"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)


DOMAIN = "your-hostname.mylabserver.com"
PORT = 8443

CERT_FILE = f"/etc/letsencrypt/live/{DOMAIN}/fullchain.pem"
KEY_FILE = f"/etc/letsencrypt/live/{DOMAIN}/privkey.pem"

server = HTTPServer(("0.0.0.0", PORT), Handler)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
)

server.socket = context.wrap_socket(
    server.socket,
    server_side=True,
)

print(f"HTTPS server listening on 0.0.0.0:{PORT}")
print(f"Open: https://{DOMAIN}:{PORT}")

server.serve_forever()

```


```
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name _;

    ssl_certificate     /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

