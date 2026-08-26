#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, tempfile, subprocess, urllib.request, urllib.parse

HOST = "127.0.0.1"
PORT = 18190

def play_file(path: str):
    ext = os.path.splitext(path.lower())[1]

    if ext in [".wav", ".aiff", ".aif", ".flac", ".ogg"]:
        subprocess.run(["paplay", path], check=True)
        return

    if ext == ".mp3":
        subprocess.run(["mpg123", "-q", path], check=True)
        return

    try:
        subprocess.run(["mpg123", "-q", path], check=True)
    except Exception:
        subprocess.run(["paplay", path], check=True)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/play":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")

        src_url = payload.get("url")
        src_file = payload.get("file")

        if not src_url and not src_file:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"{\"error\":\"missing url or file\"}")
            return

        tmp_path = None
        try:
            if src_file:
                play_file(src_file)
            else:
                parsed = urllib.parse.urlparse(src_url)
                suffix = os.path.splitext(parsed.path)[1] or ".bin"
                fd, tmp_path = tempfile.mkstemp(prefix="openclaw-tts-", suffix=suffix)
                os.close(fd)

                urllib.request.urlretrieve(src_url, tmp_path)
                play_file(tmp_path)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{\"ok\":true}")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            msg = json.dumps({"ok": False, "error": str(e)}).encode()
            self.wfile.write(msg)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
