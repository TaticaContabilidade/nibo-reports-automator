from typing import Any

from src.config import NiboRoutes


def _join_split_names(entries: list[dict[str, Any]], name_key: str) -> str:
    """Join the names of a list of category/cost-center splits into one string."""
    return ", ".join(entry.get(name_key) for entry in entries if entry.get(name_key))


def _sum_split_values(entries: list[dict[str, Any]]) -> float:
    """Sum the value of each category/cost-center split."""
    return sum(entry.get("value") or 0 for entry in entries)


def map_scheduled_item(item: dict[str, Any], route: NiboRoutes) -> dict[str, Any]:
    """Contas ainda nao vencidas (CONTAS_A_PAGAR / CONTAS_A_RECEBER)."""
    categories = item.get("categories") or []
    cost_centers = item.get("costCenters") or []
    return {
        "route": route,
        "description": item.get("description"),
        "openValue": item.get("openValue"),
        "dueDate": item.get("dueDate"),
        "name": (item.get("stakeholder") or {}).get("name"),
        "category": (item.get("category") or {}).get("name"),
        "costCenter": _join_split_names(cost_centers, "costCenterName"),
        "categoryValue": _sum_split_values(categories),
    }


def map_settled_item(item: dict[str, Any], route: NiboRoutes) -> dict[str, Any]:
    """Contas ja pagas/recebidas (CONTAS_PAGAS / CONTAS_RECEBIDAS)."""
    # Transfers between accounts are not a real income/expense entry - skip them.
    if "Transferência" in (item.get("identifier") or ""):
        return None

    categories = item.get("categories") or []
    cost_centers = item.get("costCenters") or []
    return {
        "route": route,
        "name": (item.get("stakeholder") or {}).get("name"),
        "categories": _join_split_names(categories, "categoryName"),
        "costCenter": _join_split_names(cost_centers, "costCenterName"),
        "account": (item.get("account") or {}).get("name"),
        "categoryValue": _sum_split_values(categories),
        "date": item.get("date"),
        "value": item.get("value"),
        "description": item.get("description"),
    }


MAPPERS = {
    NiboRoutes.CONTAS_A_PAGAR: map_scheduled_item,
    NiboRoutes.CONTAS_A_RECEBER: map_scheduled_item,
    NiboRoutes.CONTAS_PAGAS: map_settled_item,
    NiboRoutes.CONTAS_RECEBIDAS: map_settled_item,
}


def map_items(route: NiboRoutes, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Aplica o mapeador correto para a rota, sobre data["items"]."""
    mapper = MAPPERS[route]
    return [mapper(item, route) for item in data["items"]]
