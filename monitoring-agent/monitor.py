import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
HEALTH_URL = os.getenv("WEBSITE_HEALTH_URL", "http://127.0.0.1:8001/health")
INCIDENT_URL = os.getenv("SAFEOPS_API_URL", "http://127.0.0.1:8000/api/incidents")
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "dev-agent-token")
SERVICE_NAME = os.getenv("SERVICE_NAME", "ShopSphere")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))
incident_open = False

def report_incident(status, http_status=None, error=None):
    payload = {
        "service": SERVICE_NAME, "status": status, "http_status": http_status,
        "error": error, "source": "monitoring-agent"
    }
    response = requests.post(
        INCIDENT_URL, json=payload, headers={"X-Agent-Token": AGENT_TOKEN}, timeout=5
    )
    response.raise_for_status()
    print("Incident reported. ID:", response.json().get("id"))

def check_once():
    global incident_open
    try:
        response = requests.get(HEALTH_URL, timeout=3)
        if response.status_code == 200:
            print("ShopSphere healthy")
            incident_open = False
        else:
            print(f"ShopSphere unhealthy: HTTP {response.status_code}")
            if not incident_open:
                report_incident("unhealthy", response.status_code, response.text[:1000])
                incident_open = True
    except requests.RequestException as exc:
        print("ShopSphere unavailable:", exc)
        if not incident_open:
            try:
                report_incident("unavailable", None, str(exc)[:1000])
                incident_open = True
            except requests.RequestException as report_error:
                print("Could not report incident to SafeOps:", report_error)

if __name__ == "__main__":
    print(f"Monitoring {HEALTH_URL} every {POLL_SECONDS}s")
    while True:
        check_once()
        time.sleep(POLL_SECONDS)
