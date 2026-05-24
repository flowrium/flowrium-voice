#!/usr/bin/env python3

import argparse
import asyncio
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import websockets


DEMO_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(
        description="Serve the WeNet demo and proxy WebSocket requests to avoid browser cross-origin issues."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=18081, help="Port to bind. Default: 18081")
    parser.add_argument(
        "--ws-url",
        default=os.environ.get("WENET_WS_URL", "ws://127.0.0.1:10097"),
        help="Upstream WeNet WebSocket URL. Default: ws://127.0.0.1:10097",
    )
    return parser.parse_args()


class StaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DEMO_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


async def proxy_websocket(client_ws, upstream_url):
    async with websockets.connect(upstream_url, max_size=10_000_000) as upstream_ws:
        async def client_to_upstream():
            async for message in client_ws:
                await upstream_ws.send(message)

        async def upstream_to_client():
            async for message in upstream_ws:
                await client_ws.send(message)

        tasks = [
            asyncio.create_task(client_to_upstream()),
            asyncio.create_task(upstream_to_client()),
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        for task in done:
            task.result()


async def start_ws_proxy(host, port, upstream_url):
    async def handler(ws):
        await proxy_websocket(ws, upstream_url)

    return await websockets.serve(handler, host, port + 1, max_size=10_000_000)


async def main_async():
    args = parse_args()
    http_server = ThreadingHTTPServer((args.host, args.port), StaticHandler)
    http_server.timeout = 0.5

    ws_server = await start_ws_proxy(args.host, args.port, args.ws_url)
    print(f"Serving WeNet demo on http://{args.host}:{args.port}")
    print(f"Proxying WebSocket requests on ws://{args.host}:{args.port + 1}")
    print(f"Upstream WeNet service: {args.ws_url}")

    try:
        while True:
            http_server.handle_request()
            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        ws_server.close()
        await ws_server.wait_closed()
        http_server.server_close()


if __name__ == "__main__":
    asyncio.run(main_async())
