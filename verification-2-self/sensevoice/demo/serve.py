#!/usr/bin/env python3

import argparse
import http.client
import mimetypes
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


DEMO_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(
        description="Serve the SenseVoice demo and proxy API requests to avoid browser CORS issues."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind. Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=18080,
        help="Port to bind. Default: 18080",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("SENSEVOICE_API_URL", "http://127.0.0.1:8000"),
        help="Upstream SenseVoice API base URL. Default: http://127.0.0.1:8000",
    )
    return parser.parse_args()


def build_handler(api_url):
    upstream = urlparse(api_url.rstrip("/"))
    if upstream.scheme not in {"http", "https"}:
        raise SystemExit(f"Unsupported API URL scheme: {upstream.scheme}")

    class DemoHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DEMO_DIR), **kwargs)

        def do_GET(self):
            if self.path == "/healthz":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"ok")
                return
            if self.path.startswith("/docs") or self.path.startswith("/openapi.json"):
                self._proxy("GET")
                return
            if self.path == "/":
                self.path = "/index.html"
            return super().do_GET()

        def do_POST(self):
            if self.path.startswith("/extract_text"):
                self._proxy("POST")
                return
            self.send_error(404, "Not Found")

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def guess_type(self, path):
            if path.endswith(".js"):
                return "application/javascript; charset=utf-8"
            return mimetypes.guess_type(path)[0] or "application/octet-stream"

        def log_message(self, fmt, *args):
            print(f"[demo] {self.address_string()} - {fmt % args}")

        def _proxy(self, method):
            target_path = self.path
            if upstream.query:
                separator = "&" if "?" in target_path else "?"
                target_path = f"{target_path}{separator}{upstream.query}"

            body = None
            headers = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                content_type = self.headers.get("Content-Type")
                if content_type:
                    headers["Content-Type"] = content_type

            conn_cls = http.client.HTTPSConnection if upstream.scheme == "https" else http.client.HTTPConnection
            conn = conn_cls(upstream.hostname, upstream.port, timeout=180)

            try:
                conn.request(method, target_path, body=body, headers=headers)
                resp = conn.getresponse()
                payload = resp.read()

                self.send_response(resp.status)
                for key, value in resp.getheaders():
                    key_lower = key.lower()
                    if key_lower in {"content-length", "transfer-encoding", "connection", "content-encoding"}:
                        continue
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as exc:
                self.send_response(502)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    f'{{"error":"proxy_failed","detail":"{str(exc).replace(chr(34), chr(39))}"}}'.encode("utf-8")
                )
            finally:
                conn.close()

    return DemoHandler


def main():
    args = parse_args()
    handler = build_handler(args.api_url)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving SenseVoice demo on http://{args.host}:{args.port}")
    print(f"Proxying API requests to {args.api_url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
