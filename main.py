from flask import Flask, request, jsonify, abort
import secrets, string, json, os, time

DATA_FILE = "scripts.json"
KEYS_FILE = "keys.json"
PREMIUM_KEY = "Premium_tinhsuper16062011gm"  # example premium key -- change in production

app = Flask(__name__)

def _load_store():
    if os.path.isfile(DATA_FILE):
        return json.load(open(DATA_FILE, "r", encoding="utf-8"))
    return {}

def _save_store(s):
    json.dump(s, open(DATA_FILE, "w", encoding="utf-8"), indent=2)

def _make_id(n=8):
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))

def _make_run_key():
    return "Run_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(18))

@app.route("/", methods=["GET"])
def index():
    return "TinhSuper OBF API is running"

@app.route("/add", methods=["POST"])
def add_script():
    payload = request.get_json(force=True, silent=True) or {}
    script = payload.get("script")
    if not script:
        return jsonify({"error":"missing script"}), 400
    store = _load_store()
    s_id = _make_id(8)
    run_key = _make_run_key()
    store[s_id] = {
        "script": script,
        "created_at": int(time.time()),
        "run_key": run_key,
        "run_count": 0
    }
    _save_store(store)
    return jsonify({"id": s_id, "run_key": run_key})

@app.route("/run", methods=["GET"])
def run_script():
    s_id = request.args.get("id")
    key = request.args.get("key")
    if not s_id or not key:
        return "missing id/key", 400
    store = _load_store()
    if s_id not in store:
        return "not found", 404
    entry = store[s_id]
    if key != entry.get("run_key"):
        return "invalid key", 403
    entry["run_count"] = entry.get("run_count", 0) + 1
    _save_store(store)
    return entry["script"], 200, {"Content-Type":"text/plain; charset=utf-8"}

@app.route("/admin/get", methods=["GET"])
def admin_get():
    premium = request.args.get("premium")
    s_id = request.args.get("id")
    if premium != PREMIUM_KEY:
        return jsonify({"error":"invalid premium key"}), 403
    store = _load_store()
    if not s_id or s_id not in store:
        return jsonify({"error":"not found"}), 404
    return jsonify({"script": store[s_id]["script"], "meta": {"created_at": store[s_id]["created_at"]}})
# ---------- PING (RESET STORE) ----------
@app.route("/ping", methods=["GET"])
def ping():
    """
    - Keep Render alive
    - Xoá toàn bộ script cũ
    - Ghi đè bằng 1 script rác
    """
    global scripts

    noise_id = "noise"
    scripts = {
        noise_id: {
"run_key": "noise",
            "script": gen_noise(20),
            "created_at": int(time.time())
        }
    }

    save_json(SCRIPT_DB, scripts)
    return "pong", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
