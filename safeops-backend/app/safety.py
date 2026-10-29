def assess_incident(status: str, http_status: int | None, error: str | None):
    # Deterministic starter policy. The AI must never override these rules.
    combined = f"{status} {http_status or ''} {error or ''}".lower()

    if any(word in combined for word in ("data loss", "delete database", "ransomware")):
        return {
            "diagnosis": "Potentially destructive/security-sensitive incident; human review required.",
            "proposed_action": "collect_diagnostics",
            "risk_score": 95,
            "risk_level": "high",
            "decision": "blocked_requires_human_review",
        }

    if http_status == 500 or "unhealthy" in combined or "unavailable" in combined:
        return {
            "diagnosis": "The service health check failed; exact root cause is not yet confirmed.",
            "proposed_action": "recover_demo_service",
            "risk_score": 20,
            "risk_level": "low",
            "decision": "eligible_for_allowlisted_demo_recovery",
        }

    return {
        "diagnosis": "Abnormal status reported; more diagnostics are required.",
        "proposed_action": "collect_diagnostics",
        "risk_score": 45,
        "risk_level": "medium",
        "decision": "human_review_recommended",
    }
