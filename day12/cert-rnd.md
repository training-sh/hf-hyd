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
