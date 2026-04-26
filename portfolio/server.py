from __future__ import annotations

import json
import mimetypes
import os
import signal
import atexit
import subprocess
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MAX_CONTACT_BYTES = 64_000
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 15 * 60
DEFAULT_RATE_LIMIT_MAX = 5
LOG_PATH = ROOT / "portfolio" / "portfolio-server.log"
ERR_LOG_PATH = ROOT / "portfolio" / "portfolio-server.err.log"
PID_PATH = ROOT / "portfolio" / "portfolio-server.pid"

BLOCKED_PARTS = {".git", ".env", "__pycache__"}
BLOCKED_SUFFIXES = {".pyc", ".pyo", ".log"}
CONTACT_BUCKETS: dict[str, list[float]] = {}

mimetypes.add_type("text/javascript; charset=utf-8", ".js")
mimetypes.add_type("text/css; charset=utf-8", ".css")
mimetypes.add_type("video/webm", ".webm")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("image/avif", ".avif")


def process_exists(pid: int) -> bool:
    if pid <= 0 or pid == os.getpid():
        return False
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
        )
        return f'"{pid}"' in result.stdout or f",{pid}," in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except (OSError, SystemError):
        return False


def stop_previous_instance() -> None:
    if not PID_PATH.exists():
        return
    try:
        old_pid = int(PID_PATH.read_text(encoding="utf-8").strip())
    except ValueError:
        PID_PATH.unlink(missing_ok=True)
        return
    if not process_exists(old_pid):
        PID_PATH.unlink(missing_ok=True)
        return
    os.kill(old_pid, signal.SIGTERM)
    for _ in range(30):
        if not process_exists(old_pid):
            break
        time.sleep(0.1)


def register_instance() -> None:
    PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    stop_previous_instance()
    PID_PATH.write_text(str(os.getpid()), encoding="utf-8")

    def cleanup() -> None:
        try:
            if PID_PATH.exists() and PID_PATH.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PID_PATH.unlink()
        except OSError:
            pass

    atexit.register(cleanup)


def load_env() -> None:
    for env_path in [ROOT / ".env", ROOT / "portfolio" / ".env"]:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def clean_text(value: Any, max_length: int) -> str:
    text = str(value or "").replace("\x00", "").strip()
    return text[:max_length]


def client_ip(handler: SimpleHTTPRequestHandler) -> str:
    forwarded = handler.headers.get("CF-Connecting-IP") or handler.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return handler.client_address[0]


def rate_limited(ip: str) -> bool:
    window_seconds = int(os.getenv("CONTACT_RATE_LIMIT_WINDOW_SECONDS", str(DEFAULT_RATE_LIMIT_WINDOW_SECONDS)))
    max_requests = int(os.getenv("CONTACT_RATE_LIMIT_MAX", str(DEFAULT_RATE_LIMIT_MAX)))
    if max_requests <= 0:
        return False
    now = time.time()
    bucket = [stamp for stamp in CONTACT_BUCKETS.get(ip, []) if now - stamp < window_seconds]
    CONTACT_BUCKETS[ip] = bucket
    if len(bucket) >= max_requests:
        return True
    bucket.append(now)
    return False


def append_log(path: Path, message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")


def send_brevo_email(payload: dict[str, str]) -> tuple[bool, str]:
    email_enabled = os.getenv("CONTACT_EMAIL_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    to_email = os.getenv("CONTACT_TO_EMAIL", "davoudnikkhouy@gmail.com").strip()
    from_email = os.getenv("CONTACT_FROM_EMAIL", "").strip()
    from_name = os.getenv("CONTACT_FROM_NAME", "Davoud Nikkhouy Portfolio").strip()
    prefix = os.getenv("CONTACT_SUBJECT_PREFIX", "[Portfolio]").strip()

    if not email_enabled or not api_key or not from_email:
        append_log(LOG_PATH, f"contact inactive: {payload['email']} - {payload['subject']}")
        return False, "Email delivery is not active locally. Use the direct email link for now."

    body = {
        "sender": {"name": from_name, "email": from_email},
        "to": [{"email": to_email}],
        "replyTo": {"email": payload["email"], "name": payload["name"]},
        "subject": f"{prefix} {payload['subject']}",
        "textContent": (
            f"Name: {payload['name']}\n"
            f"Email: {payload['email']}\n"
            f"Subject: {payload['subject']}\n\n"
            f"{payload['message']}"
        ),
    }
    request = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            response_text = response.read().decode("utf-8", "replace")
            if 200 <= response.status < 300:
                try:
                    response_payload = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_payload = {}
                message_id = response_payload.get("messageId") or response_payload.get("message-id") or ""
                append_log(LOG_PATH, f"brevo accepted: status={response.status} message_id={message_id or 'unknown'} to={to_email}")
                return True, "Message accepted by email provider."
            return False, "Email provider rejected the message."
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        append_log(ERR_LOG_PATH, f"brevo http {error.code}: {detail}")
        return False, "Email provider rejected the message."
    except OSError as error:
        append_log(ERR_LOG_PATH, f"brevo error: {error}")
        return False, "Email delivery failed."


class PortfolioHandler(SimpleHTTPRequestHandler):
    server_version = "DavoudPortfolio/0.1"

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; media-src 'self' blob:; "
            "connect-src 'self'; script-src 'self'; style-src 'self'; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
        )
        super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        append_log(LOG_PATH, f"{self.address_string()} {format % args}")

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/contact":
            self.write_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        try:
            self.handle_contact()
        except ValueError as error:
            self.write_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except Exception as error:
            append_log(ERR_LOG_PATH, f"contact error: {error}")
            self.write_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Message could not be processed."})

    def handle_contact(self) -> None:
        if rate_limited(client_ip(self)):
            self.write_json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "Too many messages. Try again later."})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid request size.") from error
        if length <= 0 or length > MAX_CONTACT_BYTES:
            raise ValueError("Invalid request size.")

        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if clean_text(payload.get("website"), 200):
            self.write_json(HTTPStatus.OK, {"message": "Message received."})
            return

        message = {
            "name": clean_text(payload.get("name"), 120),
            "email": clean_text(payload.get("email"), 180),
            "subject": clean_text(payload.get("subject"), 160),
            "message": clean_text(payload.get("message"), 4000),
        }
        if not all(message.values()) or "@" not in message["email"]:
            raise ValueError("Name, email, subject, and message are required.")

        sent, status = send_brevo_email(message)
        self.write_json(HTTPStatus.OK, {"sent": sent, "message": status})

    def write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def list_directory(self, path: str) -> None:
        self.send_error(HTTPStatus.FORBIDDEN, "Directory listing is disabled.")

    def translate_path(self, path: str) -> str:
        parsed_path = unquote(urlsplit(path).path)
        if parsed_path in {"", "/"}:
            parsed_path = "/index.html"
        requested = (ROOT / parsed_path.lstrip("/")).resolve()
        try:
            requested.relative_to(ROOT)
        except ValueError:
            return str(ROOT / "__blocked__")
        if self.is_blocked(requested):
            return str(ROOT / "__blocked__")
        return str(requested)

    def is_blocked(self, path: Path) -> bool:
        try:
            relative_parts = set(path.relative_to(ROOT).parts)
        except ValueError:
            return True
        if relative_parts & BLOCKED_PARTS:
            return True
        if path.name.startswith(".") or path.suffix.lower() in BLOCKED_SUFFIXES:
            return True
        return False

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.name == "__blocked__":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found.")
            return None
        if path.is_dir():
            index = path / "index.html"
            if index.exists():
                path = index
            else:
                self.send_error(HTTPStatus.FORBIDDEN, "Directory listing is disabled.")
                return None
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found.")
            return None

        ctype = self.guess_type(str(path))
        file_size = path.stat().st_size
        range_header = self.headers.get("Range")
        if range_header:
            start, end = self.parse_range(range_header, file_size)
            if start is None:
                self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                return None
            length = end - start + 1
            handle = path.open("rb")
            handle.seek(start)
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(length))
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            self.range_remaining = length
            return handle

        handle = path.open("rb")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=3600" if "/materials/" in self.path else "no-cache")
        self.end_headers()
        return handle

    def copyfile(self, source, outputfile) -> None:
        remaining = getattr(self, "range_remaining", None)
        if remaining is None:
            super().copyfile(source, outputfile)
            return
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)
        self.range_remaining = None

    @staticmethod
    def parse_range(header: str, file_size: int) -> tuple[int | None, int | None]:
        if not header.startswith("bytes="):
            return None, None
        spec = header.removeprefix("bytes=").split(",", 1)[0].strip()
        if "-" not in spec:
            return None, None
        start_text, end_text = spec.split("-", 1)
        try:
            if start_text == "":
                suffix = int(end_text)
                if suffix <= 0:
                    return None, None
                start = max(file_size - suffix, 0)
                end = file_size - 1
            else:
                start = int(start_text)
                end = int(end_text) if end_text else file_size - 1
        except ValueError:
            return None, None
        if start < 0 or end < start or start >= file_size:
            return None, None
        return start, min(end, file_size - 1)


def main() -> int:
    load_env()
    register_instance()
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print(f"Portfolio server: http://{HOST}:{PORT}/")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
