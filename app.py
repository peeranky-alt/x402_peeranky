from flask import Flask, request, jsonify
import json, time, traceback
from agent_server import analyze_fn, send_tg, append_log

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "agent": "x402_peeranky",
        "status": "online",
        "time": int(time.time()),
        "analyzer_available": analyze_fn is not None
    })

@app.route('/invoke', methods=['POST'])
def invoke():
    try:
        payload = request.get_json(force=True)
        token = payload.get("token") or payload.get("ca")
        notify = payload.get("notify", False)

        if not token:
            return jsonify({"error": "token (contract address) required"}), 400

        start = int(time.time())
        result = analyze_fn(token)
        invocation = {
            "time": start,
            "token": token,
            "result": result,
            "notify": notify,
            "duration_s": int(time.time()) - start
        }
        append_log(invocation)

        if notify:
            try:
                summary = str(result)[:800]
                msg = f"🔔 *x402_peeranky*\nToken: `{token}`\nResult snippet:\n```\n{summary}\n```"
                send_tg(msg)
            except Exception as e:
                print("[notify] error:", e)

        return jsonify({"ok": True, "token": token, "result": result})
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({"ok": False, "error": str(e), "trace": tb[:1000]}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787)
