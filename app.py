#!/usr/bin/env python3
# ============================================================
# app.py — Drop this ONE file into C:\nli_manufacturing\
# Run:  python app.py
# Open: http://localhost:5000
# ============================================================
import re, time, random, datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ── FACTORY DATA ─────────────────────────────────────────────
MACHINES = {
    "M001": {"name": "CNC Lathe",       "status": "RUNNING", "health": 92, "temp": 68.4, "location": "Zone A"},
    "M002": {"name": "Hydraulic Press", "status": "IDLE",    "health": 78, "temp": 55.2, "location": "Zone A"},
    "M003": {"name": "Welding Robot",   "status": "WARNING", "health": 55, "temp": 84.1, "location": "Zone B"},
    "M004": {"name": "Conveyor Belt A", "status": "RUNNING", "health": 88, "temp": 42.0, "location": "Zone B"},
    "M005": {"name": "Industrial Drill","status": "OFFLINE", "health": 20, "temp": 25.0, "location": "Zone C"},
}
INVENTORY = {
    "RAW-STEEL":  {"item": "Raw Steel Sheets", "qty": 340, "unit": "sheets", "status": "OK"},
    "BOLTS-M10":  {"item": "M10 Hex Bolts",    "qty": 45,  "unit": "boxes",  "status": "LOW"},
    "HYDRO-OIL":  {"item": "Hydraulic Oil",    "qty": 18,  "unit": "litres", "status": "CRITICAL"},
    "WELD-RODS":  {"item": "Welding Rods",     "qty": 600, "unit": "units",  "status": "OK"},
    "AIR-FILTER": {"item": "HVAC Air Filters", "qty": 12,  "unit": "units",  "status": "OK"},
}
PRODUCTION = {"shift": "Morning (06:00-14:00)", "target": 500, "produced": 423,
              "defects": 8, "efficiency": 84.6, "downtime_min": 22,
              "lines_active": 3, "lines_total": 4, "supervisor": "K. Ramachandran"}
MAINTENANCE = [
    {"machine":"M005","task":"Full overhaul — bearing replacement","priority":"CRITICAL","due":"OVERDUE"},
    {"machine":"M003","task":"Temperature sensor calibration",      "priority":"HIGH",    "due":"2025-03-20"},
    {"machine":"M001","task":"Routine lubrication and inspection",  "priority":"NORMAL",  "due":"2025-04-10"},
    {"machine":"M004","task":"Belt tension check",                  "priority":"NORMAL",  "due":"2025-05-28"},
]
ALERTS = [
    {"id":"ALT-001","sev":"CRITICAL","machine":"M005","msg":"Machine OFFLINE — maintenance overdue.",        "time":"06:12"},
    {"id":"ALT-002","sev":"WARNING", "machine":"M003","msg":"High temperature detected (84.1C). Limit 80C.","time":"08:45"},
    {"id":"ALT-003","sev":"WARNING", "machine":"INV", "msg":"Hydraulic Oil CRITICAL (18L). Reorder now.",   "time":"07:00"},
    {"id":"ALT-004","sev":"INFO",    "machine":"INV", "msg":"M10 Bolts LOW (45 boxes). Reorder level 50.",  "time":"07:00"},
]

# ── KEYWORD MATCHING ─────────────────────────────────────────
INTENTS = {
    "show_status":   ["show status","status","overview","summary","dashboard"],
    "machine_health":["machine health","health report","health check","health"],
    "machine_detail":["m001","m002","m003","m004","m005","cnc","hydraulic","welding","conveyor","drill"],
    "inventory":     ["inventory","stock","spare parts","materials","warehouse"],
    "low_stock":     ["low stock","low","reorder","critical stock"],
    "maintenance":   ["maintenance","schedule","service","repair","overdue"],
    "warnings":      ["warnings","warning machines"],
    "offline":       ["offline","offline machines","machines offline"],
    "production":    ["production","output","units","efficiency","defects"],
    "alerts":        ["alerts","active alerts","any issues","notifications"],
    "help":          ["help","commands","menu","?"],
    "greeting":      ["hello","hi","hey","good morning","namaste"],
}
_ss = {"total": 0, "matched": 0, "rt": []}

def match(text):
    t0 = time.perf_counter()
    norm = re.sub(r"[^\w\s\-]", "", text.lower().strip())
    _ss["total"] += 1
    intent, kw, conf = "unknown", None, 0.0
    for i, kws in INTENTS.items():
        for k in kws:
            if k in norm:
                intent, kw = i, k
                conf = 1.0 if norm == k else (0.9 if len(k) > 8 else 0.75)
                break
        if intent != "unknown":
            break
    rt = round((time.perf_counter() - t0) * 1000, 4)
    if intent != "unknown": _ss["matched"] += 1
    _ss["rt"].append(rt)
    return {"intent": intent, "confidence": conf, "keyword": kw, "rt_ms": rt}

def build(intent, raw):
    n = raw.lower()
    if intent == "show_status":
        run = sum(1 for m in MACHINES.values() if m["status"] == "RUNNING")
        off = sum(1 for m in MACHINES.values() if m["status"] == "OFFLINE")
        cr  = sum(1 for a in ALERTS if a["sev"] == "CRITICAL")
        pct = round((PRODUCTION["produced"] / PRODUCTION["target"]) * 100, 1)
        return {"type":"status","title":"Plant Overview","data":{"running":run,"offline":off,"efficiency":PRODUCTION["efficiency"],"produced":PRODUCTION["produced"],"target":PRODUCTION["target"],"progress_pct":pct,"critical_alerts":cr,"total_alerts":len(ALERTS),"supervisor":PRODUCTION["supervisor"],"shift":PRODUCTION["shift"]}}
    if intent == "machine_health":
        return {"type":"machine_health","title":"Machine Health Report","data":[{"id":mid,"name":m["name"],"health":m["health"],"status":m["status"]} for mid,m in MACHINES.items()]}
    if intent == "machine_detail":
        t = next((mid for mid in MACHINES if mid.lower() in n), None)
        if not t:
            km = {"cnc":"M001","hydraulic":"M002","welding":"M003","conveyor":"M004","drill":"M005"}
            t = next((v for k,v in km.items() if k in n), None)
        if t and t in MACHINES:
            m = MACHINES[t]
            return {"type":"machine_detail","title":f"{t} — {m['name']}","data":{**m,"id":t}}
        return build("machine_health", raw)
    if intent == "inventory":
        return {"type":"inventory","title":"Inventory Status","data":[{"id":iid,"item":i["item"],"qty":i["qty"],"unit":i["unit"],"status":i["status"]} for iid,i in INVENTORY.items()]}
    if intent == "low_stock":
        low = [{"id":iid,"item":i["item"],"qty":i["qty"],"unit":i["unit"],"status":i["status"]} for iid,i in INVENTORY.items() if i["status"] in ("LOW","CRITICAL")]
        return {"type":"low_stock","title":"Low Stock Items","data":low}
    if intent == "maintenance":
        return {"type":"maintenance","title":"Maintenance Schedule","data":MAINTENANCE}
    if intent == "warnings":
        w = [{"id":mid,"name":m["name"],"health":m["health"],"temp":m["temp"]} for mid,m in MACHINES.items() if m["status"]=="WARNING"]
        return {"type":"warnings","title":"Machines with Warnings","data":w}
    if intent == "offline":
        o = [{"id":mid,"name":m["name"],"health":m["health"]} for mid,m in MACHINES.items() if m["status"]=="OFFLINE"]
        return {"type":"offline","title":"Offline Machines","data":o}
    if intent == "production":
        p = PRODUCTION
        return {"type":"production","title":"Production — Today","data":{**p,"progress_pct":round((p["produced"]/p["target"])*100,1),"defect_rate":round((p["defects"]/p["produced"])*100,2)}}
    if intent == "alerts":
        return {"type":"alerts","title":"Active Alerts","data":ALERTS}
    if intent == "help":
        return {"type":"help","title":"Available Commands","data":{"System":["show status","overview"],"Machines":["machine health","M001-M005","warnings","offline"],"Production":["production","efficiency","defects"],"Inventory":["inventory","stock","low stock"],"Maintenance":["maintenance","schedule","overdue"],"Alerts":["alerts","any issues"],"General":["help","exit"]}}
    if intent == "greeting":
        return {"type":"text","title":"","data":{"message":random.choice(["Hello! I am your Manufacturing Assistant. Try 'show status'.","Hi! Ask about machines, inventory, production, or alerts.","Hey! Type 'help' to see all commands."])}}
    return {"type":"unknown","title":"Not Recognised","data":{"input":raw,"suggestions":["show status","machine health","inventory","alerts","production","maintenance","help"]}}

# ── API ROUTES ───────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(silent=True) or {}
    raw  = body.get("message", "").strip()
    if not raw: return jsonify({"error": "empty"}), 400
    r    = match(raw)
    resp = build(r["intent"], raw)
    return jsonify({"intent":r["intent"],"confidence":r["confidence"],"response_time_ms":r["rt_ms"],"timestamp":datetime.datetime.now().strftime("%H:%M"),"response":resp})

@app.route("/api/stats")
def stats():
    rt = _ss["rt"]
    acc = round((_ss["matched"]/_ss["total"])*100,1) if _ss["total"] else 0
    return jsonify({"total_queries":_ss["total"],"accuracy":acc,"avg_rt":round(sum(rt)/len(rt),3) if rt else 0,"machines_running":sum(1 for m in MACHINES.values() if m["status"]=="RUNNING"),"machines_offline":sum(1 for m in MACHINES.values() if m["status"]=="OFFLINE"),"efficiency":PRODUCTION["efficiency"],"active_alerts":len(ALERTS),"critical_alerts":sum(1 for a in ALERTS if a["sev"]=="CRITICAL")})

# ── HTML (served directly — no templates folder needed) ──────
HTML = open("index.html", encoding="utf-8").read()

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    print("\n  Manufacturing NL Interface — Web Mode")
    print("  Open browser: http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)