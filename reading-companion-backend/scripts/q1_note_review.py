"""Prepare or serve an isolated Q1 v3.4 Note review. Local standard-library HTTP only."""

import argparse
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit, parse_qs
import webbrowser

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from scripts.q1_note_session import Store, prepare, rows  # noqa: E402
from scripts.q1_note_form import require  # noqa: E402


def public_case(store, rid, state):
    c = store.case_map[rid]
    ctx = c["context"]
    unit_notes = [
        r
        for r in store.read_judgments()
        if r["record_type"] == "unit_note" and r["unit_key"] == c["unit_key"]
    ]
    return dict(
        case={
            k: c[k]
            for k in (
                "record_id",
                "book",
                "chapter_title",
                "body_text",
                "source_quote",
                "unit_key",
            )
        },
        prefix=ctx["prefix"],
        recent=ctx["earlier"][-4:],
        earlier_count=max(0, len(ctx["earlier"]) - 4),
        has_following={k: bool(ctx[k]) for k in ("within_unit", "after_unit")},
        notes_status=ctx["original_notes"]["status"],
        state=state,
        unit_note=unit_notes[-1]["remarks"] if unit_notes else "",
    )


def server(store, port=8767):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Never log source text, judgments or URL identifiers.

        def respond(self, value, status=200, mime="application/json; charset=utf-8"):
            data = (
                value
                if isinstance(value, bytes)
                else json.dumps(value, ensure_ascii=False).encode()
            )
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(data)

        def origin_ok(self, write=False):
            expected = f"127.0.0.1:{self.server.server_port}"
            require(self.headers.get("Host") == expected, "只允许本机地址")
            if write:
                require(
                    self.headers.get("Origin") == "http://" + expected
                    and self.headers.get("Content-Type") == "application/json",
                    "请求来源不符",
                )

        def do_GET(self):
            try:
                self.origin_ok()
                url = urlsplit(self.path)
                assets = {
                    "/": "q1-note-annotator.html",
                    "/app.js": "q1-note-annotator.js",
                    "/style.css": "q1-note-annotator.css",
                }
                if url.path in assets:
                    name = assets[url.path]
                    mime = (
                        "text/html"
                        if name.endswith(".html")
                        else "text/javascript"
                        if name.endswith(".js")
                        else "text/css"
                    )
                    return self.respond(
                        (BACKEND / "tools" / name).read_bytes(),
                        mime=mime + "; charset=utf-8",
                    )
                if url.path == "/bootstrap":
                    journal = store.read_judgments()
                    progress = rows(store.folder / "progress.jsonl")
                    return self.respond(
                        dict(
                            form=store.form,
                            purpose=store.manifest["session_purpose"],
                            record_ids=store.manifest["record_ids"],
                            last_id=progress[-1]["record_id"] if progress else None,
                            completed=list(
                                {
                                    r["record_id"]
                                    for r in journal
                                    if r["record_type"] == "marginalia"
                                }
                            ),
                        )
                    )
                if url.path == "/earlier":
                    rid = parse_qs(url.query)["id"][0]
                    require(rid in store.case_map, "未知条目")
                    return self.respond(store.case_map[rid]["context"]["earlier"][:-4])
                raise ValueError("未知路径")
            except (ValueError, KeyError, TypeError) as e:
                self.respond(dict(error=str(e)), 400)

        def do_POST(self):
            try:
                self.origin_ok(write=True)
                size = int(self.headers.get("Content-Length", "0"))
                require(0 < size <= 200000, "请求长度无效")
                data = json.loads(self.rfile.read(size))
                require(urlsplit(self.path).path == "/action", "未知路径")
                rid = data["id"]
                if data["action"] == "unit_note":
                    store.unit_note(
                        store.case_map[rid]["unit_key"], data["values"]["remarks"]
                    )
                    return self.respond(dict(saved=True))
                state = store.action(
                    rid,
                    data["action"],
                    data.get("values"),
                    data.get("version"),
                    data.get("active_ms", 0),
                )
                result = public_case(store, rid, state)
                if data["action"] == "following":
                    result["following"] = store.case_map[rid]["context"][
                        data["values"]["scope"]
                    ]
                if data["action"] == "notes":
                    result["notes"] = store.case_map[rid]["context"]["original_notes"]
                self.respond(result)
            except (ValueError, KeyError, TypeError, OSError) as e:
                self.respond(dict(error=str(e)), 400)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for command in ("prepare", "launch"):
        x = sub.add_parser(command)
        x.add_argument("--source", required=True, type=Path)
        x.add_argument("--session", required=True, type=Path)
        x.add_argument("--book-root", action="append", required=True, type=Path)
        x.add_argument("--seed", type=int, default=20261115)
        x.add_argument("--purpose", choices=("formal", "test"), default="formal")
        x.add_argument("--test-mark", action="append")
        if command == "launch":
            x.add_argument("--port", type=int, default=8767)
            x.add_argument("--no-open", action="store_true")
    x = sub.add_parser("serve")
    x.add_argument("session", type=Path)
    x.add_argument("--port", type=int, default=8767)
    x.add_argument("--no-open", action="store_true")
    args = p.parse_args()
    if args.command in ("prepare", "launch"):
        if args.command == "prepare" or not args.session.exists():
            prepare(
                args.source,
                args.session,
                args.book_root,
                args.seed,
                args.purpose,
                args.test_mark,
            )
        else:
            existing = Store(args.session).manifest
            require(
                existing["session_purpose"] == args.purpose
                and existing["randomization"]["seed"] == args.seed,
                "已有会话用途或种子不符，请另选目录",
            )
            require(
                existing["source_mixed_sha256"]
                == sha256((args.source / "mixed.json").read_bytes()).hexdigest(),
                "已有会话属于另一批次，请另选目录",
            )
            require(
                not args.test_mark
                or set(existing["record_ids"]) == set(args.test_mark),
                "已有测试会话条目不符",
            )
    if args.command in ("serve", "launch"):
        srv = server(Store(args.session), args.port)
        url = f"http://127.0.0.1:{srv.server_port}"
        print(f"Q1 Note review: {url}", flush=True)
        if not args.no_open:
            webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.server_close()


if __name__ == "__main__":
    main()
