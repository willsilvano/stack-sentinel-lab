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
    raise NotImplementedError("Ex05 ainda nao implementado")
