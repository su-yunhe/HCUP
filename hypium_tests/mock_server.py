"""本地模拟 NeteaseCloudMusicApi 的 /search 与 /song/detail，供分页自测使用。

真实服务器看不到请求次数，"滑到底不自动请求""连点不重复请求"这类断言只能靠这里的请求日志。
响应结构与真实接口实测一致（baseline-notes 7.3）：
- 正常页 `{"result": {"songs": [...], "hasMore": bool, "songCount": n}, "code": 200}`
- 零结果 / 超出范围 `{"result": {"songCount": 0}, "code": 200}`（没有 songs、hasMore）
关键字末尾的数字即结果总数，例如 `pga75` 有 75 首，歌名为 `pga75-歌曲1` ~ `pga75-歌曲75`。
"""
from __future__ import annotations

import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 3999


class MockState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self.lock:
            self.requests: list[tuple[str, int | None, int | None]] = []
            self.delay_first = 0.0          # offset == 0 的响应延时（秒）
            self.delay_more = 0.0           # offset > 0 的响应延时（秒）
            self.failures: dict[int, list[str]] = {}  # offset -> 依次消费的失败方式
            self.empty_pages: set[int] = set()        # 返回空 songs + hasMore=true 的 offset

    def search_offsets(self, keyword: str) -> list[int | None]:
        with self.lock:
            return [o for k, _, o in self.requests if k == keyword]

    def search_requests(self, keyword: str) -> list[tuple[str, int | None, int | None]]:
        with self.lock:
            return [r for r in self.requests if r[0] == keyword]


STATE = MockState()


def _song(keyword: str, i: int) -> dict:
    return {
        "id": abs(hash((keyword, i))) % 10_000_000 + 1,
        "name": f"{keyword}-歌曲{i + 1}",
        "artists": [{"id": 1, "name": "模拟歌手"}],
        "duration": 200_000,
        "album": {"id": 1, "name": "模拟专辑"},
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: D401 - 静默
        pass

    def _send_json(self, body: dict) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self._handle()

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        self._handle()

    def _handle(self) -> None:
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        if url.path == "/song/detail":
            self._send_json({"songs": [{"al": {"picUrl": ""}}], "code": 200})
            return
        if url.path != "/search":
            self._send_json({"code": 404})
            return

        keyword = qs.get("keywords", [""])[0]
        limit = int(qs["limit"][0]) if "limit" in qs else None
        offset = int(qs["offset"][0]) if "offset" in qs else None
        off = offset or 0
        with STATE.lock:
            STATE.requests.append((keyword, limit, offset))
            delay = STATE.delay_first if off == 0 else STATE.delay_more
            queue = STATE.failures.get(off) or []
            failure = queue.pop(0) if queue else None
            empty_page = off in STATE.empty_pages
        if delay:
            time.sleep(delay)

        if failure == "drop":       # 网络层失败：不回响应直接断开
            self.close_connection = True
            self.connection.shutdown(2)
            return
        if failure == "code400":    # 业务失败：与真实接口纯空格响应相同
            self._send_json({"code": 400})
            return
        if failure == "noresult":   # 结构异常：有 code 但没有 result
            self._send_json({"code": 200})
            return

        if not keyword.strip():
            self._send_json({"code": 400})
            return
        m = re.search(r"(\d+)$", keyword)
        total = int(m.group(1)) if m else 0
        size = limit or 30
        if empty_page:
            self._send_json({"result": {"songs": [], "hasMore": True, "songCount": total}, "code": 200})
            return
        if off >= total:
            self._send_json({"result": {"songCount": 0}, "code": 200})
            return
        end = min(off + size, total)
        songs = [_song(keyword, i) for i in range(off, end)]
        self._send_json({"result": {"songs": songs, "hasMore": end < total, "songCount": total}, "code": 200})


class MockServer:
    def __init__(self, port: int = PORT) -> None:
        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.httpd.daemon_threads = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
