from datetime import datetime, timezone
import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import AGENT_TOKEN, OPERATOR_TOKEN, SIMULATOR_TOKEN, SIMULATOR_BASE_URL
from .db import connection, init_db, row_to_dict
from .schemas import IncidentIn
from .safety import assess_incident

app = FastAPI(title="SafeOps API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "X-Agent-Token", "X-Operator-Token"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/system/health")
def system_health():
    return {"status": "healthy", "service": "safeops-backend"}

@app.post("/api/incidents")
def create_incident(payload: IncidentIn, x_agent_token: str | None = Header(default=None)):
    if x_agent_token != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid agent token")
    result = assess_incident(payload.status, payload.http_status, payload.error)
    with connection() as conn:
        cur = conn.execute(
            """INSERT INTO incidents
            (service,status,http_status,error,source,diagnosis,proposed_action,risk_score,risk_level,decision,recovery_status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (payload.service,payload.status,payload.http_status,payload.error,payload.source,
             result["diagnosis"],result["proposed_action"],result["risk_score"],result["risk_level"],
             result["decision"],"pending")
        )
        row = conn.execute("SELECT * FROM incidents WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)

@app.get("/api/incidents")
def list_incidents():
    with connection() as conn:
        rows = conn.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 100").fetchall()
    return [row_to_dict(row) for row in rows]

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: int):
    with connection() as conn:
        row = conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    return row_to_dict(row)

@app.post("/api/incidents/{incident_id}/recover")
def recover_demo_incident(incident_id: int, x_operator_token: str | None = Header(default=None)):
    if x_operator_token != OPERATOR_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid operator token")
    with connection() as conn:
        row = conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = row_to_dict(row)
    if incident["proposed_action"] != "recover_demo_service":
        raise HTTPException(status_code=403, detail="Action is not allowlisted")
    if incident["risk_level"] != "low" or incident["risk_score"] >= 30:
        raise HTTPException(status_code=403, detail="Risk policy blocked this action")

    try:
        action = requests.post(
            f"{SIMULATOR_BASE_URL}/internal/demo-actions/recover",
            headers={"X-Simulator-Token": SIMULATOR_TOKEN}, timeout=5
        )
        action.raise_for_status()
        health = requests.get(f"{SIMULATOR_BASE_URL}/health", timeout=3)
        recovered = health.status_code == 200
        error = None
    except requests.RequestException as exc:
        recovered, error = False, str(exc)

    status = "resolved" if recovered else "recovery_failed_escalate"
    now = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        conn.execute("UPDATE incidents SET recovery_status=?, updated_at=? WHERE id=?",
                     (status, now, incident_id))
        updated = conn.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
    return {
        "incident": row_to_dict(updated),
        "action": "recover_demo_service",
        "health_check": "passed" if recovered else "failed",
        "message": "Recovery verified." if recovered else "Recovery failed; escalate to a human.",
        "error": error,
    }
