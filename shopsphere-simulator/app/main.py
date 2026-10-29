import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

load_dotenv()
SIMULATOR_TOKEN = os.getenv("SIMULATOR_TOKEN", "dev-simulator-token")
app = FastAPI(title="ShopSphere Demo Simulator")
_is_healthy = True

@app.get("/")
def home():
    return {"service": "ShopSphere demo simulator", "healthy": _is_healthy}

@app.get("/health")
def health():
    if not _is_healthy:
        return JSONResponse(status_code=500, content={
            "status": "unhealthy", "error": "Simulated application failure"
        })
    return {"status": "healthy", "service": "shopsphere-simulator"}

@app.post("/demo/fail")
def simulate_failure():
    global _is_healthy
    _is_healthy = False
    return {"message": "Simulated failure enabled", "healthy": _is_healthy}

@app.post("/demo/restore")
def restore_manually():
    global _is_healthy
    _is_healthy = True
    return {"message": "Simulator restored manually", "healthy": _is_healthy}

@app.post("/internal/demo-actions/recover")
def allowlisted_recovery(x_simulator_token: str | None = Header(default=None)):
    global _is_healthy
    if x_simulator_token != SIMULATOR_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid simulator token")
    # Deliberately limited demo action; no operating-system commands are executed.
    _is_healthy = True
    return {"action": "recover_demo_service", "status": "success", "healthy": _is_healthy}
