from flask import Flask, request, jsonify, make_response
import secrets, string, json, os, time

DATA_FILE = "scripts.json"
PREMIUM_KEY = "Premium_tinhsuper16062011gm"  # đổi khi production

app = Flask(__name__)

# ================== UTIL ==================

def load_store():
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_store(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_id(n=8):
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))

def make_run_key():
    return "Run_" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(18))

def raw_text_response(text: str):
    """
    Trả về RAW text, tắt hoàn toàn nén (FIX br / gzip)
    """
    resp = make_response(text, 200)
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Content-Encoding"] = "identity"
    return resp

# ================== ROUTES ==================

@app.route("/", methods=["GET"])
def index():
    return "TinhSuper OBF API is running", 200

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

# ---------- ADD SCRIPT ----------
@app.route("/add", methods=["POST"])
def add_script():
    payload = request.get_json(force=True, silent=True) or {}
    script = payload.get("script")

    if not script:
        return jsonify({"error": "missing script"}), 400

    store = load_store()
    s_id = make_id()
    run_key = make_run_key()

    store[s_id] = {
        "script": script,
        "created_at": int(time.time()),
        "run_key": run_key,
        "run_count": 0
    }

    save_store(store)

    return jsonify({
        "id": s_id,
        "run_key": run_key
    })

# ---------- RUN SCRIPT ----------
@app.route("/run", methods=["GET"])
def run_script():
    s_id = request.args.get("id")
    key = request.args.get("key")

    if not s_id or not key:
        return "missing id/key", 400

    store = load_store()
    entry = store.get(s_id)

    if not entry:
        return "not found", 404

    if key != entry["run_key"]:
        return "invalid key", 403

    entry["run_count"] += 1
    save_store(store)

    # ⭐ TRẢ RAW LUA – KHÔNG BROTLI
    return raw_text_response(entry["script"])

# ---------- ADMIN GET ----------
@app.route("/admin/get", methods=["GET"])
def admin_get():
    premium = request.args.get("premium")
    s_id = request.args.get("id")

    if premium != PREMIUM_KEY:
        return jsonify({"error": "invalid premium key"}), 403

    store = load_store()
    entry = store.get(s_id)

    if not entry:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "script": entry["script"],
        "meta": {
            "created_at": entry["created_at"],
"run_count": entry["run_count"]
        }
    })

# ================== MAIN ==================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        threaded=True
    )
