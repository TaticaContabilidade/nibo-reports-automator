import requests
from datetime import datetime, timedelta
from typing import Any
from src.config import CLIENTES, NiboRoutes


class RouteRequest:
    def __init__(self, cliente: str):
        self.api_token = CLIENTES[cliente]
        self.routes: list[NiboRoutes] = list(NiboRoutes)

    def routes_requests(self) -> list[dict[str, Any]]:
        data: list[dict[str, Any]] = []
        date = datetime.now().strftime("%Y-%m-%d")
        retro_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        plus_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        for route in self.routes:
            if "_A_" in route.name:
                params = {"$filter": f"date ge {date} and date le {plus_date}"}
            else:
                params = {"$filter": f"date ge {retro_date} and date le {date}"}

            response = requests.get(
                route.value,
                headers={"ApiToken": self.api_token},
                params=params,
            )
            data.append(response.json())

        return data
