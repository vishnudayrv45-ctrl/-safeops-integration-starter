# SafeOps Integration Starter

This starter connects a ShopSphere demo app, a monitoring agent, and a SafeOps FastAPI backend with SQLite. It does not overwrite your existing React frontend.

## Requirements
Python 3.10+. For your existing frontend, use your current Node.js setup.

## Start backend (Terminal 1)
```bash
cd safeops-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Start ShopSphere simulator (Terminal 2)
```bash
cd shopsphere-simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

## Start monitoring agent (Terminal 3)
```bash
cd monitoring-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python monitor.py
```

## Demo
1. Open http://127.0.0.1:8000/docs
2. Open http://127.0.0.1:8001/docs
3. Simulate a failure: `curl -X POST http://127.0.0.1:8001/demo/fail`
4. Wait 5 seconds; the agent reports an incident.
5. List incidents: `curl http://127.0.0.1:8000/api/incidents`
6. Use the incident ID in:
   `curl -X POST http://127.0.0.1:8000/api/incidents/1/recover -H "X-Operator-Token: dev-operator-token"`

Recovery is restricted to a single demo endpoint and does not execute shell commands.

## Existing frontend
Copy `frontend-snippets/src/services/safeopsApi.ts` into your frontend at `src/services/safeopsApi.ts`. Do not replace your current `App.tsx`, pages, store, or types until we inspect their existing code. You can set `VITE_SAFEOPS_API_URL=http://127.0.0.1:8000` in your frontend `.env`.

## Safety
These are local development tokens only. Keep the demo on localhost, change tokens before any shared deployment, and never let an LLM execute arbitrary shell commands. The AI can recommend; policy enforcement must independently authorize actions.
