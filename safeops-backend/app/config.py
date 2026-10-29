import os
from dotenv import load_dotenv
load_dotenv()

AGENT_TOKEN = os.getenv("AGENT_TOKEN", "dev-agent-token")
SIMULATOR_TOKEN = os.getenv("SIMULATOR_TOKEN", "dev-simulator-token")
OPERATOR_TOKEN = os.getenv("OPERATOR_TOKEN", "dev-operator-token")
SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
DATABASE_PATH = os.getenv("DATABASE_PATH", "safeops.db")
