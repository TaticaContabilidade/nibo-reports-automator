from typing import Any

from src.config import NiboRoutes


def mapear_agendada(item: dict[str, Any]) -> dict[str, Any]:
    """Contas ainda nao vencidas (CONTAS_A_PAGAR / CONTAS_A_RECEBER)."""
    return {
        "descricao": item.get("description"),
        "valor": item.get("value"),
        "valor_aberto": item.get("openValue"),
        "vencimento": item.get("dueDate"),
        "fornecedor": (item.get("stakeholder") or {}).get("name"),
        "categoria": (item.get("category") or {}).get("name"),
        "pago": item.get("isPaid"),
    }


def mapear_liquidada(item: dict[str, Any]) -> dict[str, Any]:
    """Contas ja pagas/recebidas (CONTAS_PAGAS / CONTAS_RECEBIDAS)."""
    return {
        "account": item.get("account"),
        "categories": item.get("categories"),
        "date": item.get("date"),
        "value": item.get("value"),
    }


MAPEADORES = {
    NiboRoutes.CONTAS_A_PAGAR: mapear_agendada,
    NiboRoutes.CONTAS_A_RECEBER: mapear_agendada,
    NiboRoutes.CONTAS_PAGAS: mapear_liquidada,
    NiboRoutes.CONTAS_RECEBIDAS: mapear_liquidada,
}


def mapear(route: NiboRoutes, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Aplica o mapeador correto para a rota, sobre data["items"]."""
    mapeador = MAPEADORES[route]
    return list(map(mapeador, data["items"]))
