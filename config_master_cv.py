from __future__ import annotations

import json
import os
import signal
import atexit
import re
import shutil
import subprocess
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required. Install it with: python -m pip install PyYAML")
    raise SystemExit(1)

import build


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config_SDNT.yaml"
STATE_PATH = ROOT / "states.json"
PREVIEW_DIR = build.CV_DIR / "preview"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8010
MAX_BODY_BYTES = 2_000_000
PID_PATH = ROOT / "portfolio" / "master-cv-server.pid"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{CONFIG_PATH.name} must contain a YAML mapping.")
    return data


def save_config(config: dict[str, Any]) -> None:
    lines = CONFIG_PATH.read_text(encoding="utf-8-sig").splitlines()
    line_map = include_line_map()
    flags = include_flags(config)

    for key, include in flags.items():
        line_number = line_map.get(key)
        if line_number is None or line_number >= len(lines):
            continue
        lines[line_number] = re.sub(
            r"^(\s*include\s*:\s*)(?:true|false|True|False|yes|no)(.*)$",
            rf"\1{'true' if include else 'false'}\2",
            lines[line_number],
        )

    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        state = {"openNodes": [], "search": ""}
        save_state(state)
        return state
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        state = {"openNodes": [], "search": ""}
    if not isinstance(state, dict):
        state = {"openNodes": [], "search": ""}
    open_nodes = state.get("openNodes", [])
    if not isinstance(open_nodes, list):
        open_nodes = []
    search = state.get("search", "")
    if not isinstance(search, str):
        search = ""
    return {"openNodes": open_nodes, "search": search}


def save_state(state: dict[str, Any]) -> None:
    open_nodes = state.get("openNodes", [])
    search = state.get("search", "")
    clean = {
        "openNodes": [str(item) for item in open_nodes] if isinstance(open_nodes, list) else [],
        "search": search if isinstance(search, str) else "",
    }
    STATE_PATH.write_text(json.dumps(clean, indent=2) + "\n", encoding="utf-8")


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
        import time

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


def path_key(path: list[Any]) -> str:
    return json.dumps(path, separators=(",", ":"))


def include_flags(value: Any, path: list[Any] | None = None) -> dict[str, bool]:
    path = path or []
    flags: dict[str, bool] = {}
    if isinstance(value, dict):
        if "include" in value:
            flags[path_key(path)] = bool(value.get("include"))
        for key, child in value.items():
            if key == "include":
                continue
            flags.update(include_flags(child, [*path, key]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            flags.update(include_flags(child, [*path, index]))
    return flags


def include_line_map() -> dict[str, int]:
    root = yaml.compose(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    result: dict[str, int] = {}

    def walk(node: Any, path: list[Any]) -> None:
        if isinstance(node, yaml.MappingNode):
            pairs = [(key_node.value, value_node) for key_node, value_node in node.value]
            for key, value_node in pairs:
                if key == "include":
                    result[path_key(path)] = value_node.start_mark.line
                    break
            for key, value_node in pairs:
                if key == "include":
                    continue
                walk(value_node, [*path, key])
        elif isinstance(node, yaml.SequenceNode):
            for index, child in enumerate(node.value):
                walk(child, [*path, index])

    if root is not None:
        walk(root, [])
    return result


def display_key(key: Any) -> str:
    text = str(key)
    text = re.sub(r"[_-]+", " ", text).strip()
    return text[:1].upper() + text[1:]


def item_label(path: list[Any], node: Any) -> str:
    if not path:
        return "config"
    last = path[-1]
    if isinstance(last, int):
        preview = preview_value(node)
        if preview:
            return preview[:80]
        parent = display_key(path[-3] if len(path) >= 3 and path[-2] == "items" else path[-2] if len(path) >= 2 else "Item")
        return f"{parent} {last + 1}"
    return display_key(last)


def preview_value(node: Any) -> str:
    if not isinstance(node, dict):
        return str(node)
    for key in ["display_name", "title", "name", "degree", "company", "institution", "venue", "email"]:
        value = node.get(key)
        if isinstance(value, dict) and "value" in value:
            return str(value.get("value", ""))
        if isinstance(value, str):
            return value
    if "value" in node:
        return str(node.get("value", ""))
    if "items" in node and isinstance(node["items"], list):
        return f"{len(node['items'])} items"
    return ""


def path_label(path: list[Any]) -> str:
    if not path:
        return "config"
    last = path[-1]
    if isinstance(last, int):
        return f"Item {last + 1}"
    return display_key(last)


def include_nodes(value: Any, path: list[Any] | None = None) -> list[dict[str, Any]]:
    path = path or []
    nodes: list[dict[str, Any]] = []

    if isinstance(value, dict):
        if "include" in value:
            nodes.append(
                {
                    "path": path,
                    "label": item_label(path, value),
                    "include": bool(value.get("include")),
                    "preview": preview_value(value),
                    "children": include_child_nodes(value, path),
                }
            )
            return nodes
        nodes.extend(include_child_nodes(value, path))
        return nodes

    if isinstance(value, list):
        for index, item in enumerate(value):
            nodes.extend(include_nodes(item, [*path, index]))

    return nodes


def include_child_nodes(value: dict[str, Any], path: list[Any]) -> list[dict[str, Any]]:
    children: list[dict[str, Any]] = []
    for key, child in value.items():
        if key == "include":
            continue
        if key == "value":
            continue
        if isinstance(child, list):
            for index, item in enumerate(child):
                children.extend(include_nodes(item, [*path, key, index]))
        else:
            children.extend(include_nodes(child, [*path, key]))
    return children


def node_at(config: Any, path: list[Any]) -> Any:
    node = config
    for part in path:
        if isinstance(node, list) and isinstance(part, int):
            node = node[part]
        elif isinstance(node, dict) and isinstance(part, str):
            node = node[part]
        else:
            raise KeyError(path)
    return node


def apply_include_changes(config: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    for change in changes:
        path = change.get("path")
        if not isinstance(path, list):
            continue
        node = node_at(config, path)
        if isinstance(node, dict) and "include" in node:
            node["include"] = bool(change.get("include"))


def export_cv(config: dict[str, Any]) -> dict[str, Any]:
    save_config(config)
    build.CV_DIR.mkdir(parents=True, exist_ok=True)
    build.CV_TEX.write_text(build.render_cv(config), encoding="utf-8")
    build.write_site_data(config)
    try:
        pdf_ok = build.compile_pdf()
        compile_error = ""
    except Exception as error:
        pdf_ok = False
        compile_error = str(error)
    preview_pages = generate_pdf_preview() if pdf_ok else preview_payload().get("pages", [])
    return {
        "pdf_ok": pdf_ok,
        "error": compile_error,
        "tex": "/" + build.CV_TEX.relative_to(ROOT).as_posix(),
        "pdf": "/" + build.CV_PDF.relative_to(ROOT).as_posix() if build.CV_PDF.exists() else "",
        "data": "/" + build.SITE_DATA.relative_to(ROOT).as_posix(),
        "preview_pages": preview_pages,
    }


def generate_pdf_preview() -> list[str]:
    if not build.CV_PDF.exists():
        return []
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return []

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for old_page in PREVIEW_DIR.glob("page-*.png"):
        old_page.unlink()

    prefix = PREVIEW_DIR / "page"
    result = subprocess.run(
        [pdftoppm, "-png", "-r", "135", str(build.CV_PDF), str(prefix)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "pdftoppm failed").strip())

    return [
        "/" + page.relative_to(ROOT).as_posix()
        for page in sorted(PREVIEW_DIR.glob("page-*.png"))
    ]


def preview_payload() -> dict[str, Any]:
    pages = [
        "/" + page.relative_to(ROOT).as_posix()
        for page in sorted(PREVIEW_DIR.glob("page-*.png"))
    ]
    if build.CV_PDF.exists() and not pages:
        pages = generate_pdf_preview()
    return {
        "pdf": "/" + build.CV_PDF.relative_to(ROOT).as_posix() if build.CV_PDF.exists() else "",
        "pages": pages,
    }


def json_response(handler: SimpleHTTPRequestHandler, status: HTTPStatus, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: SimpleHTTPRequestHandler) -> dict[str, Any]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        length = 0
    if length <= 0 or length > MAX_BODY_BYTES:
        raise ValueError("Invalid request size.")
    return json.loads(handler.rfile.read(length).decode("utf-8"))


PAGE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Master CV Config</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f3f5f7;
        --panel: #ffffff;
        --text: #16181d;
        --muted: #5d6673;
        --line: #d7dde5;
        --soft-line: #e8ecf1;
        --accent: #0f6b78;
        --accent-strong: #0a4e58;
        --accent-soft: #e6f3f5;
        --green: #247a48;
        --amber: #96651f;
        --red: #b42318;
        --danger: #b42318;
        --shadow: 0 12px 30px rgba(20, 28, 38, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: linear-gradient(180deg, #f8fafb 0%, var(--bg) 280px);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      header {
        position: sticky;
        top: 0;
        z-index: 10;
        border-bottom: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(14px);
      }
      .bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        max-width: 1520px;
        margin: 0 auto;
        padding: 12px 20px;
      }
      .brand { display: flex; flex-direction: column; gap: 3px; min-width: 220px; }
      h1 { margin: 0; font-size: 20px; line-height: 1.2; letter-spacing: 0; }
      .subtitle { color: var(--muted); font-size: 13px; }
      .actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
      button, a.button {
        min-height: 36px;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 7px 12px;
        background: #fff;
        color: var(--text);
        font: inherit;
        text-decoration: none;
        cursor: pointer;
        transition: border-color 120ms ease, background 120ms ease, color 120ms ease, box-shadow 120ms ease;
      }
      button:hover, a.button:hover { border-color: #aeb8c5; box-shadow: 0 2px 8px rgba(20, 28, 38, 0.08); }
      button.primary {
        border-color: var(--accent);
        background: var(--accent);
        color: #fff;
      }
      button.primary:hover { background: var(--accent-strong); }
      button:disabled { opacity: 0.55; cursor: default; }
      main {
        display: grid;
        grid-template-columns: minmax(420px, 560px) minmax(0, 1fr);
        gap: 18px;
        max-width: 1520px;
        height: calc(100vh - 65px);
        margin: 0 auto;
        padding: 18px 20px;
        overflow: hidden;
      }
      .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        min-width: 0;
        box-shadow: var(--shadow);
      }
      .left { overflow: hidden; }
      .templates {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        padding: 12px;
        border-bottom: 1px solid var(--line);
        background: #fbfcfd;
      }
      .template {
        display: grid;
        gap: 4px;
        text-align: left;
        min-height: 74px;
        border-color: var(--soft-line);
        background: #fff;
      }
      .template strong { font-size: 13px; }
      .template span { color: var(--muted); font-size: 12px; line-height: 1.3; }
      .template[data-template="minimal"] { border-left: 4px solid var(--green); }
      .template[data-template="industry"] { border-left: 4px solid var(--accent); }
      .template[data-template="academic"] { border-left: 4px solid var(--amber); }
      .template[data-template="full"] { border-left: 4px solid #6b7280; }
      .tools {
        display: grid;
        grid-template-columns: 1fr auto auto auto;
        gap: 8px;
        padding: 12px;
        border-bottom: 1px solid var(--line);
      }
      input[type="search"] {
        width: 100%;
        min-height: 38px;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 8px 10px;
        font: inherit;
      }
      #tree {
        height: calc(100vh - 265px);
        overflow: auto;
        padding: 10px 12px 18px;
      }
      details {
        border-left: 1px solid var(--soft-line);
        margin-left: 12px;
        padding-left: 12px;
      }
      details.root {
        border-left: 0;
        margin-left: 0;
        padding-left: 0;
        border-bottom: 1px solid var(--soft-line);
        padding-bottom: 7px;
        margin-bottom: 7px;
      }
      summary {
        list-style: none;
        display: grid;
        grid-template-columns: 18px 1fr;
        gap: 8px;
        align-items: start;
        min-height: 36px;
        padding: 5px 0;
        cursor: pointer;
      }
      summary::-webkit-details-marker { display: none; }
      .caret {
        width: 18px;
        height: 18px;
        margin-top: 2px;
        border-radius: 4px;
        color: var(--muted);
        font-size: 13px;
        line-height: 18px;
        text-align: center;
      }
      details[open] > summary .caret::before { content: "v"; }
      details:not([open]) > summary .caret::before { content: ">"; }
      details:not(.has-children) > summary .caret::before { content: ""; }
      .row {
        display: grid;
        grid-template-columns: 36px 1fr;
        gap: 10px;
        align-items: start;
      }
      input[type="checkbox"] {
        appearance: none;
        width: 34px;
        height: 20px;
        margin: 1px 0 0;
        border: 1px solid #b7c1cc;
        border-radius: 999px;
        background: #e9edf2;
        position: relative;
      }
      input[type="checkbox"]::after {
        content: "";
        position: absolute;
        top: 2px;
        left: 2px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #fff;
        box-shadow: 0 1px 3px rgba(20, 28, 38, 0.22);
        transition: transform 120ms ease;
      }
      input[type="checkbox"]:checked {
        border-color: var(--accent);
        background: var(--accent);
      }
      input[type="checkbox"]:checked::after { transform: translateX(14px); }
      .meta { min-width: 0; }
      .label {
        display: flex;
        gap: 8px;
        align-items: baseline;
        min-width: 0;
      }
      .name { font-weight: 650; }
      .root > summary .name { font-size: 15px; }
      .path {
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 12px;
        overflow-wrap: anywhere;
      }
      .preview {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.35;
        overflow-wrap: anywhere;
        margin-top: 2px;
      }
      .node.hidden { display: none; }
      .right {
        display: grid;
        grid-template-rows: auto 1fr;
        min-height: 0;
        height: 100%;
        overflow: hidden;
      }
      .status {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 12px 14px;
        border-bottom: 1px solid var(--line);
        color: var(--muted);
        font-size: 14px;
        background: #fbfcfd;
      }
      .status strong { color: var(--text); }
      .pill {
        display: inline-flex;
        align-items: center;
        min-height: 26px;
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 3px 9px;
        background: #fff;
        color: var(--muted);
        font-size: 12px;
      }
      .pdf-preview {
        width: 100%;
        height: 100%;
        min-height: 0;
        overflow: auto;
        padding: 22px;
        background:
          radial-gradient(circle at 50% 0%, rgba(15, 107, 120, 0.08), transparent 28rem),
          #eef1f5;
      }
      .pdf-preview__empty {
        display: grid;
        min-height: 620px;
        place-items: center;
        color: var(--muted);
        text-align: center;
      }
      .pdf-page {
        display: block;
        width: min(100%, 920px);
        height: auto;
        margin: 0 auto 22px;
        border-radius: 4px;
        background: #fff;
        box-shadow: 0 10px 28px rgba(20, 28, 38, 0.18);
      }
      .error { color: var(--danger); }
      @media (max-width: 980px) {
        main { grid-template-columns: 1fr; }
        .templates { grid-template-columns: 1fr; }
        .tools { grid-template-columns: 1fr 1fr; }
        .tools input { grid-column: 1 / -1; }
        #tree { height: 56vh; }
        .right { min-height: 80vh; }
      }
    </style>
  </head>
  <body>
    <header>
      <div class="bar">
        <div class="brand">
          <h1>Master CV Config</h1>
          <span class="subtitle">Select CV content from config_SDNT.yaml and export the generated PDF.</span>
        </div>
        <div class="actions">
          <button type="button" id="save">Save</button>
          <button type="button" class="primary" id="export">Export LaTeX + PDF</button>
          <a class="button" href="/materials/CV/CV.pdf" target="_blank" rel="noreferrer">Open PDF</a>
        </div>
      </div>
    </header>
    <main>
      <section class="panel left">
        <div class="templates" aria-label="CV templates">
          <button type="button" class="template" data-template="minimal">
            <strong>Minimal</strong>
            <span>Core identity, contact, skills, recent work, and education.</span>
          </button>
          <button type="button" class="template" data-template="industry">
            <strong>Industry Robotics</strong>
            <span>Experience, technical stack, selected projects, and education.</span>
          </button>
          <button type="button" class="template" data-template="academic">
            <strong>Academic Research</strong>
            <span>Research profile, publications, education, references, and core skills.</span>
          </button>
          <button type="button" class="template" data-template="full">
            <strong>Full Master CV</strong>
            <span>Everything that has content in the source config.</span>
          </button>
        </div>
        <div class="tools">
          <input id="search" type="search" placeholder="Filter fields" />
          <button type="button" id="all-on">All on</button>
          <button type="button" id="all-off">All off</button>
          <button type="button" id="clear-changes">Reset edits</button>
        </div>
        <div id="tree"></div>
      </section>
      <section class="panel right">
        <div class="status">
          <span id="status-text">Loading config...</span>
          <span class="pill"><strong id="count-on">0</strong>&nbsp;included /&nbsp;<strong id="count-total">0</strong>&nbsp;toggles</span>
        </div>
        <div id="pdf-preview" class="pdf-preview" aria-label="CV PDF page preview">
          <div class="pdf-preview__empty">Loading PDF preview...</div>
        </div>
      </section>
    </main>
    <script>
      const tree = document.querySelector("#tree");
      const statusText = document.querySelector("#status-text");
      const countOn = document.querySelector("#count-on");
      const countTotal = document.querySelector("#count-total");
      const pdfPreview = document.querySelector("#pdf-preview");
      const changes = new Map();
      let openNodes = new Set();
      let stateSaveTimer = 0;
      let autoExportTimer = 0;
      let autoExportRunning = false;
      let nodes = [];

      const templates = {
        full(path, node) {
          const last = path[path.length - 1];
          if (node.preview === "" && ["link", "paper", "phone", "final_grade", "thesis"].includes(last)) return false;
          return true;
        },
        minimal(path) {
          const key = path.join(".");
          const root = path[0];
          if (root === "Profile") return true;
          if (["Email", "Phone", "Portfolio", "Skills", "Work_experience", "Education"].includes(root)) return true;
          if (root === "social_media_links") return path[1] === 0 || path[1] === 1;
          if (path[0] === "site") return true;
          const keepRoots = ["profile", "skills", "work_experience", "education"];
          if (path.length === 1) return keepRoots.includes(path[0]);
          if (key.startsWith("profile.")) {
            return [
              "profile.display_name",
              "profile.headline",
              "profile.location",
              "profile.about",
              "profile.contact",
              "profile.contact.email",
              "profile.contact.phone",
              "profile.contact.portfolio",
              "profile.links",
              "profile.links.items.0",
              "profile.links.items.0.name",
              "profile.links.items.0.url",
              "profile.links.items.1",
              "profile.links.items.1.name",
              "profile.links.items.1.url",
            ].includes(key);
          }
          if (key.startsWith("skills.")) return true;
          if (key.startsWith("work_experience.")) {
            if (path[0] === "work_experience" && path[1] === "items" && Number.isInteger(path[2])) return path[2] === 0;
            return path[2] === 0 || path.length <= 2;
          }
          if (key.startsWith("education.")) {
            if (path[0] === "education" && path[1] === "items" && Number.isInteger(path[2])) return path[2] <= 1;
            const field = path[path.length - 1];
            return path.length <= 3 || ["degree", "field", "branch", "institution", "location", "display_date"].includes(field);
          }
          return false;
        },
        industry(path) {
          const key = path.join(".");
          const root = path[0];
          if (root === "Profile") return true;
          if (["Email", "Phone", "Portfolio", "Projects", "Skills", "Work_experience", "Education"].includes(root)) return true;
          if (root === "social_media_links") return path[1] === 0 || path[1] === 1 || path[1] === 2 || path[1] === 3;
          if (path[0] === "site") return true;
          const keepRoots = ["profile", "skills", "work_experience", "projects", "education"];
          if (path.length === 1) return keepRoots.includes(path[0]);
          if (key.startsWith("profile.")) {
            if (key.startsWith("profile.links.items.")) return path[3] === 0 || path[3] === 1;
            return !["first_name", "last_name", "home_address"].includes(path[path.length - 1]);
          }
          return key.startsWith("skills.") || key.startsWith("work_experience.") || key.startsWith("projects.") || key.startsWith("education.");
        },
        academic(path) {
          const key = path.join(".");
          const root = path[0];
          if (root === "Profile") return true;
          if (["Email", "Phone", "Portfolio", "Skills", "Work_experience", "Education", "Publications", "Referees"].includes(root)) return true;
          if (root === "social_media_links") return path[1] === 1 || path[1] === 2 || path[1] === 3 || path[1] === 4;
          if (path[0] === "site") return true;
          const keepRoots = ["profile", "skills", "work_experience", "education", "publications", "referees"];
          if (path.length === 1) return keepRoots.includes(path[0]);
          if (key.startsWith("profile.")) {
            if (key.startsWith("profile.links.items.")) return path[3] === 1 || path[3] === 2;
            return !["first_name", "last_name", "home_address"].includes(path[path.length - 1]);
          }
          return key.startsWith("skills.") || key.startsWith("work_experience.") || key.startsWith("education.") || key.startsWith("publications.") || key.startsWith("referees.");
        },
      };

      function escapeHtml(value = "") {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }

      function pathText(path) {
        return Array.isArray(path) ? path.map((part, index) => Number.isInteger(part) ? `[${part}]` : (index === 0 ? part : `.${part}`)).join("") : "";
      }

      function pathKey(path) {
        return JSON.stringify(path);
      }

      function flatten(items, result = []) {
        for (const item of items) {
          result.push(item);
          flatten(item.children || [], result);
        }
        return result;
      }

      function descendantNodes(node, result = []) {
        for (const child of node.children || []) {
          result.push(child);
          descendantNodes(child, result);
        }
        return result;
      }

      function currentInclude(node) {
        const key = pathKey(node.path);
        return changes.has(key) ? changes.get(key).include : node.include;
      }

      function setNodeInclude(node, include) {
        changes.set(pathKey(node.path), { path: node.path, include });
      }

      function nodeByKey(key) {
        return flatten(nodes).find((node) => pathKey(node.path) === key);
      }

      function saveOpenNodes() {
        saveEditorState();
      }

      function collectState() {
        return {
          openNodes: Array.from(openNodes),
          search: document.querySelector("#search").value,
        };
      }

      function saveEditorState() {
        window.clearTimeout(stateSaveTimer);
        stateSaveTimer = window.setTimeout(() => {
          postJson("/api/state", collectState()).catch(() => {});
        }, 150);
      }

      function renderNode(node, root = false) {
        const key = pathKey(node.path);
        const checked = currentInclude(node);
        const children = (node.children || []).map((child) => renderNode(child)).join("");
        const openAttr = openNodes.has(key) ? "open" : "";
        return `
          <details class="node ${root ? "root" : ""} ${children ? "has-children" : ""}" ${openAttr} data-key="${escapeHtml(key)}">
            <summary>
              <span class="caret"></span>
              <span class="row">
                <input type="checkbox" data-path="${escapeHtml(key)}" ${checked ? "checked" : ""} />
                <span class="meta">
                  <span class="label">
                    <span class="name">${escapeHtml(node.label)}</span>
                    <span class="path">${escapeHtml(pathText(node.path))}</span>
                  </span>
                  ${node.preview ? `<span class="preview">${escapeHtml(node.preview)}</span>` : ""}
                </span>
              </span>
            </summary>
            ${children}
          </details>
        `;
      }

      function render() {
        tree.innerHTML = nodes.map((node) => renderNode(node, true)).join("");
        tree.querySelectorAll("details.node").forEach((detail) => {
          detail.addEventListener("toggle", () => {
            if (detail.open) {
              openNodes.add(detail.dataset.key);
            } else {
              openNodes.delete(detail.dataset.key);
            }
            saveOpenNodes();
          });
        });
        tree.querySelectorAll("input[type=checkbox]").forEach((input) => {
          input.addEventListener("click", (event) => event.stopPropagation());
          input.addEventListener("change", () => {
            const node = nodeByKey(input.dataset.path);
            if (node) {
              setNodeInclude(node, input.checked);
            } else {
              changes.set(input.dataset.path, { path: JSON.parse(input.dataset.path), include: input.checked });
            }
            render();
            scheduleAutoExport();
          });
        });
        updateCounts();
        filterTree();
      }

      function updateCounts() {
        const all = flatten(nodes);
        let included = 0;
        for (const node of all) {
          const key = pathKey(node.path);
          const checked = currentInclude(node);
          if (checked) included += 1;
        }
        countOn.textContent = included;
        countTotal.textContent = all.length;
      }

      function collectChanges() {
        return Array.from(changes.values());
      }

      async function postJson(url, payload) {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(result.error || "Request failed.");
        return result;
      }

      async function saveOnly() {
        window.clearTimeout(autoExportTimer);
        statusText.textContent = "Saving config_SDNT.yaml...";
        const result = await postJson("/api/save", { changes: collectChanges() });
        changes.clear();
        nodes = result.nodes;
        render();
        statusText.textContent = "Saved config_SDNT.yaml.";
      }

      async function exportAndRefreshPreview(reason = "Exporting CV...") {
        if (!changes.size && reason !== "Exporting CV...") return;
        statusText.textContent = reason;
        const result = await postJson("/api/export", { changes: collectChanges() });
        changes.clear();
        nodes = result.nodes;
        render();
        const stamp = Date.now();
        renderPdfPreview(Array.isArray(result.files.preview_pages) ? result.files.preview_pages : [], stamp);
        if (result.files.pdf_ok) {
          statusText.innerHTML = `Exported <strong>${escapeHtml(result.files.pdf)}</strong>`;
        } else {
          const detail = result.files.error ? ` ${escapeHtml(result.files.error)}` : "";
          statusText.innerHTML = `<span class="error">LaTeX export finished, but PDF generation failed.${detail}</span>`;
        }
      }

      async function exportCv() {
        await exportAndRefreshPreview("Exporting CV...");
      }

      function scheduleAutoExport() {
        window.clearTimeout(autoExportTimer);
        statusText.textContent = "Changes pending. Preview will update automatically...";
        autoExportTimer = window.setTimeout(async () => {
          if (autoExportRunning) return;
          autoExportRunning = true;
          try {
            await exportAndRefreshPreview("Applying changes to preview...");
          } catch (error) {
            statusText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
          } finally {
            autoExportRunning = false;
          }
        }, 900);
      }

      function renderPdfPreview(pages, stamp = Date.now()) {
        if (!pages || !pages.length) {
          pdfPreview.innerHTML = `
            <div class="pdf-preview__empty">
              <div>
                <strong>No page preview is available.</strong><br />
                Export the CV first, or make sure pdftoppm is installed.
              </div>
            </div>
          `;
          return;
        }
        pdfPreview.innerHTML = pages
          .map((page, index) => `<img class="pdf-page" src="${escapeHtml(page)}?t=${stamp}" alt="CV page ${index + 1}" loading="lazy" />`)
          .join("");
      }

      async function loadPdfPreview() {
        try {
          const response = await fetch("/api/preview");
          const result = await response.json();
          renderPdfPreview(result.pages || []);
        } catch (error) {
          pdfPreview.innerHTML = `<div class="pdf-preview__empty"><span class="error">${escapeHtml(error.message)}</span></div>`;
        }
      }

      function setAll(include) {
        for (const node of flatten(nodes)) {
          changes.set(pathKey(node.path), { path: node.path, include });
        }
        render();
        scheduleAutoExport();
      }

      function applyTemplate(name) {
        const template = templates[name];
        if (!template) return;
        for (const node of flatten(nodes)) {
          changes.set(pathKey(node.path), { path: node.path, include: template(node.path, node) });
        }
        render();
        const label = document.querySelector(`[data-template="${name}"] strong`)?.textContent || name;
        statusText.textContent = `${label} template applied. Preview will update automatically...`;
        scheduleAutoExport();
      }

      function resetEdits() {
        window.clearTimeout(autoExportTimer);
        changes.clear();
        render();
        statusText.textContent = "Unsaved edits reset.";
      }

      function filterTree() {
        const needle = document.querySelector("#search").value.trim().toLowerCase();
        tree.querySelectorAll(".node").forEach((element) => {
          const text = element.textContent.toLowerCase();
          element.classList.toggle("hidden", needle && !text.includes(needle));
        });
        saveEditorState();
      }

      async function init() {
        try {
          const [configResponse, stateResponse] = await Promise.all([
            fetch("/api/config"),
            fetch("/api/state"),
          ]);
          const result = await configResponse.json();
          const state = await stateResponse.json();
          nodes = result.nodes;
          const savedOpenNodes = Array.isArray(state.openNodes) ? state.openNodes : [];
          openNodes = new Set(savedOpenNodes.length ? savedOpenNodes : nodes.map((node) => pathKey(node.path)));
          document.querySelector("#search").value = typeof state.search === "string" ? state.search : "";
          render();
          loadPdfPreview();
          statusText.textContent = "Loaded config_SDNT.yaml.";
        } catch (error) {
          statusText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
        }
      }

      document.querySelector("#save").addEventListener("click", () => saveOnly().catch((error) => {
        statusText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
      }));
      document.querySelector("#export").addEventListener("click", () => exportCv().catch((error) => {
        statusText.innerHTML = `<span class="error">${escapeHtml(error.message)}</span>`;
      }));
      document.querySelector("#all-on").addEventListener("click", () => setAll(true));
      document.querySelector("#all-off").addEventListener("click", () => setAll(false));
      document.querySelector("#clear-changes").addEventListener("click", resetEdits);
      document.querySelectorAll("[data-template]").forEach((button) => {
        button.addEventListener("click", () => applyTemplate(button.dataset.template));
      });
      document.querySelector("#search").addEventListener("input", filterTree);
      init();
    </script>
  </body>
</html>
"""


class MasterCvHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            body = PAGE.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/config":
            try:
                config = load_config()
                json_response(self, HTTPStatus.OK, {"nodes": include_nodes(config)})
            except Exception as error:  # pragma: no cover - visible in browser.
                json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return
        if self.path == "/api/preview":
            try:
                json_response(self, HTTPStatus.OK, preview_payload())
            except Exception as error:  # pragma: no cover - visible in browser.
                json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return
        if self.path == "/api/state":
            try:
                json_response(self, HTTPStatus.OK, load_state())
            except Exception as error:  # pragma: no cover - visible in browser.
                json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/state":
            try:
                save_state(read_json(self))
                json_response(self, HTTPStatus.OK, load_state())
            except Exception as error:  # pragma: no cover - visible in browser.
                json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})
            return
        if self.path not in {"/api/save", "/api/export"}:
            json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found."})
            return
        try:
            payload = read_json(self)
            config = load_config()
            changes = payload.get("changes", [])
            if not isinstance(changes, list):
                raise ValueError("changes must be a list.")
            apply_include_changes(config, changes)
            if self.path == "/api/export":
                files = export_cv(config)
            else:
                save_config(config)
                files = {}
            json_response(self, HTTPStatus.OK, {"nodes": include_nodes(config), "files": files})
        except Exception as error:  # pragma: no cover - visible in browser.
            json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})


def main() -> int:
    host = os.getenv("HOST", DEFAULT_HOST)
    port = int(os.getenv("PORT", str(DEFAULT_PORT)))
    register_instance()
    os.chdir(ROOT)
    server = ThreadingHTTPServer((host, port), MasterCvHandler)
    url = f"http://{host}:{port}/"
    print(f"Master CV editor: {url}")
    print("Edit checkboxes, then Save or Export LaTeX + PDF.")
    if os.getenv("OPEN_BROWSER", "1") != "0":
        webbrowser.open(url)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
