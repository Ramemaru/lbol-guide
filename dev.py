#!/usr/bin/env python3
"""One-command local Decap CMS editor with automatic preview rebuilds.

Requires Python packages in requirements.txt and Node.js >=20.
The local Decap proxy is bound to localhost and uses local files, not GitHub.
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser

import build

ROOT = Path(__file__).resolve().parent
PORT = 8000


def fingerprints() -> dict[str, int]:
    result = {}
    for folder in ("content", "templates", "assets", "admin"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file():
                try:
                    result[str(path)] = path.stat().st_mtime_ns
                except FileNotFoundError:
                    continue
    return result


def watch_content(stop: threading.Event) -> None:
    previous = fingerprints()
    while not stop.wait(1):
        changed = fingerprints()
        if changed == previous:
            continue
        previous = changed
        try:
            build.main()
            print("\n[preview] 記事の変更を反映しました。ブラウザを再読み込みしてください。", flush=True)
        except Exception as exc:
            # A partially saved file must not terminate the editor.
            print(f"\n[preview] ビルドエラー：{exc}", flush=True)


def proxy_is_listening() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 8081), timeout=0.5):
            return True
    except OSError:
        return False


def open_when_ready(stop: threading.Event) -> None:
    # `npx` may download a package the first time. Never open the editor
    # before the local proxy is listening or Decap could try GitHub login.
    for _ in range(120):
        if stop.wait(1):
            return
        if proxy_is_listening():
            webbrowser.open(f"http://127.0.0.1:{PORT}/admin/")
            print(f"編集画面：http://127.0.0.1:{PORT}/admin/", flush=True)
            return
    print("Decap のローカルサーバーが起動しませんでした。npx のログを確認してください。", flush=True)


def main() -> int:
    npx = shutil.which("npx")
    if not npx:
        print("Node.js 20 以降が必要です：https://nodejs.org/ を確認してください。")
        return 1
    build.main()
    args = [npx, "--yes", "decap-server"]
    if os.name == "nt":
        args = ["cmd", "/c", npx, "--yes", "decap-server"]
    print("Decap のローカルサーバーを起動中...", flush=True)
    process = subprocess.Popen(args, cwd=ROOT)
    stop = threading.Event()
    server = None
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist")))
        threading.Thread(target=watch_content, args=(stop,), daemon=True).start()
        threading.Thread(target=open_when_ready, args=(stop,), daemon=True).start()
        print(f"サイト：http://127.0.0.1:{PORT}/", flush=True)
        print("終了するときは Ctrl+C。記事は content/ に保存されます。", flush=True)
        server.serve_forever(poll_interval=0.5)
    except (KeyboardInterrupt, OSError) as exc:
        if isinstance(exc, OSError):
            print(f"起動できませんでした：{exc}", file=sys.stderr)
            return 1
        print("\n終了します。")
    finally:
        stop.set()
        if server:
            server.server_close()
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
