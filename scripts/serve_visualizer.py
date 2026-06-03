#!/usr/bin/env python3
"""Serve a visualizer folder and accept selected-node Markdown exports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class VisualizerHandler(SimpleHTTPRequestHandler):
    server_version = "SkillFlowVisualizer/1.0"
    quiet_paths = (
        "/",
        "/flows.json",
        "/flow.json",
        "/runtime-state.json",
        "/flow-",
        "/api/health",
        "/api/selection-state",
    )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"ok": True})
            return
        if path == "/api/selection-state":
            latest_state = self._exports_dir() / "selection-state-latest.json"
            if latest_state.exists():
                try:
                    self._send_json(json.loads(latest_state.read_text(encoding="utf-8")))
                except json.JSONDecodeError:
                    self._send_json({
                        "ok": False,
                        "selectedCount": 0,
                        "selectedNodes": [],
                        "selectionSummary": "选择状态正在更新，请稍后重试。",
                    })
            else:
                self._send_json({
                    "ok": True,
                    "selectedCount": 0,
                    "selectedNodes": [],
                    "selectionSummary": "当前没有选中节点。",
                })
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/selection-state":
            self._handle_selection_state()
            return
        if path != "/api/selection-export":
            self.send_error(404, "Unknown endpoint")
            return

        payload = self._read_json_body()
        if payload is None:
            return

        markdown = str(payload.get("markdown") or "").strip()
        if not markdown:
            self.send_error(400, "Missing markdown")
            return

        exports_dir = self._exports_dir()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        md_path = exports_dir / f"selected-nodes-{stamp}.md"
        json_path = exports_dir / f"selected-nodes-{stamp}.json"
        latest_md = exports_dir / "selected-nodes-latest.md"
        latest_json = exports_dir / "selected-nodes-latest.json"

        enriched = {
            **payload,
            "savedAt": datetime.now(timezone.utc).isoformat(),
            "markdownPath": str(md_path),
            "jsonPath": str(json_path),
        }
        self._write_text_atomic(md_path, markdown + "\n")
        self._write_text_atomic(json_path, json.dumps(enriched, ensure_ascii=False, indent=2) + "\n")
        self._write_text_atomic(latest_md, markdown + "\n")
        self._write_text_atomic(latest_json, json.dumps(enriched, ensure_ascii=False, indent=2) + "\n")

        self._send_json({
            "ok": True,
            "markdownPath": str(md_path),
            "jsonPath": str(json_path),
            "latestMarkdownPath": str(latest_md),
            "latestJsonPath": str(latest_json),
        })

    def _read_json_body(self):
        try:
            length = int(self.headers.get("content-length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(400, f"Invalid JSON: {exc}")
            return None

    def _exports_dir(self) -> Path:
        root = Path(self.directory).resolve()
        exports_dir = root / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        return exports_dir

    def _handle_selection_state(self) -> None:
        payload = self._read_json_body()
        if payload is None:
            return
        exports_dir = self._exports_dir()
        latest_state = exports_dir / "selection-state-latest.json"
        enriched = {
            **payload,
            "ok": True,
            "savedAt": datetime.now(timezone.utc).isoformat(),
            "statePath": str(latest_state),
        }
        self._write_text_atomic(latest_state, json.dumps(enriched, ensure_ascii=False, indent=2) + "\n")
        self._send_json({
            "ok": True,
            "statePath": str(latest_state),
            "selectedCount": enriched.get("selectedCount", 0),
        })

    def _write_text_atomic(self, path: Path, text: str) -> None:
        tmp_path = path.with_name(f".{path.name}.tmp")
        tmp_path.write_text(text, encoding="utf-8")
        tmp_path.replace(path)

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        path = urlparse(self.path).path
        is_quiet_get = self.command == "GET" and (
            path in self.quiet_paths or any(path.startswith(prefix) for prefix in self.quiet_paths if prefix.endswith("-"))
        )
        if is_quiet_get:
            return
        super().log_message(format, *args)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve a Skill Flow Visualizer with export bridge support.")
    parser.add_argument("--root", default=".", help="Visualizer folder to serve.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=5188, help="Port to bind.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        parser.error(f"Root does not exist: {root}")

    handler = lambda *handler_args, **handler_kwargs: VisualizerHandler(
        *handler_args,
        directory=str(root),
        **handler_kwargs,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving visualizer: {root}")
    print(f"URL: http://{args.host}:{args.port}/")
    print("Selection exports will be written to: exports/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
