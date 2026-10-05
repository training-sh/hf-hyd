"""Loopback-only API for the OpenAPI/auth labs; no cloud services."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import unquote
import json
from course import get_order


def start_order_api(bearer_token=None):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status = 200
            if bearer_token and self.headers.get("Authorization") != "Bearer " + bearer_token:
                status, payload = 401, {"error": "Missing or invalid bearer token"}
            elif self.path.startswith("/orders/"):
                payload = get_order(unquote(self.path.split("/orders/", 1)[1]))
                status = 404 if "error" in payload else 200
            else:
                status, payload = 404, {"error": "Not found"}
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def order_spec(base_url, secured=False):
    spec = {
        "openapi": "3.0.3", "info": {"title": "Demo Orders", "version": "1.0"},
        "servers": [{"url": base_url}],
        "paths": {"/orders/{order_id}": {"get": {
            "operationId": "lookup_order_api", "summary": "Look up a demo order by ID",
            "parameters": [{"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {"200": {"description": "Order details", "content": {"application/json": {"schema": {"type": "object", "properties": {
                "order_id": {"type": "string"}, "status": {"type": "string"}, "total": {"type": "number"}, "currency": {"type": "string"}}}}}},
                "401": {"description": "Unauthorized"}, "404": {"description": "Unknown order"}}
        }}}}
    if secured:
        spec["components"] = {"securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}}}
        spec["security"] = [{"BearerAuth": []}]
    return spec
