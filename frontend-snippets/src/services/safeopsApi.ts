export type SafeOpsIncident = {
  id: number;
  service: string;
  status: string;
  http_status: number | null;
  error: string | null;
  source: string;
  diagnosis: string;
  proposed_action: string;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | string;
  decision: string;
  recovery_status: string;
  created_at: string;
  updated_at: string;
};

const API_BASE = import.meta.env.VITE_SAFEOPS_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) throw new Error(`SafeOps API ${response.status}: ${await response.text()}`);
  return response.json() as Promise<T>;
}

export const getIncidents = () => request<SafeOpsIncident[]>("/api/incidents");
export const getIncident = (id: number) => request<SafeOpsIncident>(`/api/incidents/${id}`);
export const getBackendHealth = () =>
  request<{ status: string; service: string }>("/api/system/health");

// Demo only: never put a production operator secret in browser code.
export const requestDemoRecovery = (id: number, operatorToken: string) =>
  request<{ incident: SafeOpsIncident; action: string; health_check: string; message: string }>(
    `/api/incidents/${id}/recover`,
    { method: "POST", headers: { "X-Operator-Token": operatorToken } }
  );
