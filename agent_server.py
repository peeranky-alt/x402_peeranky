#!/usr/bin/env python3
"""
agent_server.py
Lightweight HTTP wrapper that exposes your local analyzer as an "agent" endpoint.

How it works:
- Loads config.json for bot token + chat id + port + options
- Tries to import analyze_token(token) from known modules
- Exposes:
    GET  /status         -> simple health + info
    POST /invoke         -> {"token":"0x...","notify":true}
- Saves invocation logs to agent_invocations.json
"""

import json, time, os, traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from io import BytesIO

# -------- load config ----------
CFG_PATH = "config.json"
if not os.path.exists(CFG_PATH):
    print("ERROR: config.json not found. Create it in the same folder as agent_server.py")
    raise SystemExit(1)

with open(CFG_PATH, "r") as f:
    cfg = json.load(f)

BOT_TOKEN = cfg.get("telegram_bot_token")
CHAT_ID = cfg.get("telegram_chat_id")
PORT = int(cfg.get("agent_port", 8787))
REQUIRE_PAYMENT = bool(cfg.get("agent_require_payment", False))
ALLOWED_CALLERS = cfg.get("agent_allowed_callers", [])
INVOKE_API_KEY = cfg.get("agent_api_key", "")

LOG_FILE = "agent_invocations.json"

# -------- import analyze_token ----------
analyze_fn = None
possible_modules = ["analyzer", "profiler", "wallet_profiler", "wallet_scraper", "scraper", "analyzer_v2"]

for mod in possible_modules:
    try:
        m = __import__(mod)
        if hasattr(m, "analyze_token"):
            analyze_fn = getattr(m, "analyze_token")
            print(f"[agent] using analyze_token from module: {mod}")
            break
        for alt in ("analyze", "analyze_token_main", "profile_token", "run_analyze"):
            if hasattr(m, alt):
                analyze_fn = getattr(m, alt)
                print(f"[agent] using {alt} from module: {mod}")
                break
        if analyze_fn:
            break
    except Exception:
        pass

if analyze_fn is None:
    for mod in ("bot", "utility", "watchlist"):
        try:
            m = __import__(mod)
            for alt in ("analyze_token", "analyze"):
                if hasattr(m, alt):
                    analyze_fn = getattr(m, alt)
                    print(f"[agent] using {alt} from module: {mod}")
                    break
            if analyze_fn:
                break
        except Exception:
            pass

if analyze_fn is None:
    print("[agent] Warning: Could not find analyze_token function.")
else:
    print("[agent] analyze function ready.")

# -------- helpers ----------
def send_tg(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[tg] missing BOT_TOKEN or CHAT_ID, skipped send.")
        return
    try:
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        r = requests.post(url, json=payload, timeout=8)
        if r.status_code != 200:
            print("[tg] send failed:", r.status_code, r.text)
    except Exception as e:
        print("[tg] send exception:", e)

def append_log(entry: dict):
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                old = json.load(f) or []
        else:
            old = []
    except Exception:
        old = []
    old.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(old, f, indent=2)

# -------- HTTP handler ----------
class AgentHandler(BaseHTTPRequestHandler):
    def _set_json(self, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/status":
            info = {
                "status": "ok",
                "time": int(time.time()),
                "analyzer_available": analyze_fn is not None,
                "allowed_callers": ALLOWED_CALLERS or "any"
            }
            self._set_json(200)
            self.wfile.write(json.dumps(info).encode())
            return
        if parsed.path == "/logs":
            try:
                with open(LOG_FILE, "r") as f:
                    data = json.load(f)
            except Exception:
                data = []
            self._set_json(200)
            self.wfile.write(json.dumps({"invocations": data[-50:]}).encode())
            return
        self._set_json(404)
        self.wfile.write(json.dumps({"error": "not found"}).encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        client_ip = self.client_address[0]
        if ALLOWED_CALLERS and client_ip not in ALLOWED_CALLERS:
            self._set_json(403)
            self.wfile.write(json.dumps({"error": "caller not allowed", "client_ip": client_ip}).encode())
            return

        headers = self.headers
        if INVOKE_API_KEY:
            key = headers.get("X-API-KEY") or parse_qs(parsed.query).get("api_key", [None])[0]
            if key != INVOKE_API_KEY:
                self._set_json(401)
                self.wfile.write(json.dumps({"error": "invalid api key"}).encode())
                return

        if parsed.path == "/invoke":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b""
            try:
                payload = json.loads(body.decode() or "{}")
            except:
                payload = {}

            token = payload.get("token") or payload.get("ca") or payload.get("contract")
            notify = payload.get("notify", False)
            paid = payload.get("paid", False)

            if REQUIRE_PAYMENT and not paid:
                self._set_json(402)
                self.wfile.write(json.dumps({"error": "payment required"}).encode())
                return

            if not token:
                self._set_json(400)
                self.wfile.write(json.dumps({"error": "token required"}).encode())
                return

            start = int(time.time())
            invocation = {
                "time": start,
                "token": token,
                "client_ip": client_ip,
                "notify": notify,
                "result": None,
                "error": None
            }

            try:
                if analyze_fn is None:
                    raise RuntimeError("analyze function not available on server")

                # ✅ FIXED: Always wrap token into dict for analyzer.py
                try:
                    result = analyze_fn({"ca": token})
                except Exception:
                    try:
                        result = analyze_fn(token)
                    except TypeError:
                        result = analyze_fn(token, None)

                invocation["result"] = result

                if notify:
                    try:
                        summary = json.dumps(result)[:800] if isinstance(result, dict) else str(result)[:800]
                        msg = f"🔔 *Agent invocation*\nToken: `{token}`\nResult snippet:\n```\n{summary}\n```"
                        send_tg(msg)
                    except Exception as e:
                        print("[agent] tg notify error:", e)

                invocation["duration_s"] = int(time.time()) - start
                append_log(invocation)
                self._set_json(200)
                self.wfile.write(json.dumps({"ok": True, "token": token, "result": result}).encode())

            except Exception as e:
                tb = traceback.format_exc()
                invocation["error"] = str(e)
                append_log(invocation)
                self._set_json(500)
                self.wfile.write(json.dumps({"ok": False, "error": str(e), "trace": tb[:2000]}).encode())
            return

        self._set_json(404)
        self.wfile.write(json.dumps({"error": "not found"}).encode())

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, AgentHandler)
    print(f"[agent] Server running on 0.0.0.0:{PORT} (invoke POST /invoke with JSON {{'token':'0x...','notify':true}} )")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("[agent] stopping server")

if __name__ == "__main__":
    run_server()
