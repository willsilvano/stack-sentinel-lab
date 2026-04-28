from typing import Any, Dict, Optional

from stack_sentinel.clients.mock_service_client import MockServiceClient


def fetch_ticket_context(ticket_id: str, client: Optional[MockServiceClient] = None) -> Dict[str, Any]:
    """Contrato do Ex02: retorna contexto normalizado de um ticket."""
    if client is None:
        client = MockServiceClient()
    try:
        if not ticket_id:
            return {"ok": False, "error": "ticket_id é obrigatório"}

        response = client.get_ticket(ticket_id)

        if not response.get("ok"):
            return {"ok": False, "error": response.get("error", "erro desconhecido")}

        data = response["data"]
        return {
            "ok": True,
            "id": data["id"],
            "summary": data["summary"],
            "severity": data["severity"],
            "service": data["service"],
            "status": data["status"],
            "build_id": data["build_id"],
        }
    except Exception as exc:
        return {"ok": False, "error": "erro inesperado"}


def fetch_build_status(build_id: str, client: Optional[MockServiceClient] = None) -> Dict[str, Any]:
    """Contrato do Ex05: retorna status normalizado de um build."""
    if client is None:
        client = MockServiceClient()
    try:
        if not build_id or not build_id.strip():
            return {"ok": False, "error": "build_id é obrigatório"}
        if not build_id.startswith("BLD-"):
            return {"ok": False, "error": f"build_id inválido: '{build_id}'. Esperado formato BLD-<número>"}

        response = client.get_build(build_id)

        if not response.get("ok"):
            return {"ok": False, "error": response.get("error", "erro desconhecido")}

        data = response["data"]
        return {
            "ok": True,
            "id": data["id"],
            "status": data["status"],
            "service": data["service"],
            "branch": data["branch"],
            "failed_step": data["failed_step"],
            "log_excerpt": data["log_excerpt"],
        }
    except Exception:
        return {"ok": False, "error": "erro inesperado"}
