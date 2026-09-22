from datetime import datetime, timedelta
from typing import Any
from src.config import CLIENTES, NiboRoutes
from logs.authentication_logs import NiboAuthError, NiboTimeoutError
from src.userful.map_dict import map_items
import requests
import time


MAX_TRY = 3

class RouteRequest:
    """Cliente para as 4 rotas de contas (a pagar/a receber/pagas/recebidas)
    da API do NIBO, autenticado com o token de um cliente da Tatica."""

    def __init__(self, cliente: str):
        """
        Args:
            cliente: chave presente em CLIENTES (ex: "eva clinica", "dr mikle").

        Raises:
            KeyError: se `cliente` nao existir em CLIENTES.
        """
        self.api_token = CLIENTES[cliente]
        self.routes: list[NiboRoutes] = list(NiboRoutes)

    def routes_requests(self, timeout=10) -> list[dict[str, Any]]:
        """Busca as 4 rotas do NIBO, uma requisicao por rota.

        Contas ainda nao vencidas (nome contem "_A_", ex: CONTAS_A_PAGAR) usam
        uma janela de data para frente (hoje ate +7 dias); as demais, ja
        liquidadas, usam uma janela para tras (-7 dias ate hoje).

        Em caso de timeout, a requisicao e reprocessada via `retry_requests`.

        Returns:
            Lista achatada com os itens de todas as rotas ja mapeados
            (ver src/userful/map_dict.py), sem separacao por rota.

        Raises:
            NiboAuthError: se a API responder 401 (token invalido/expirado).
            NiboTimeoutError: se todas as tentativas de retry esgotarem.
        """
        data: list[dict[str, Any]] = []
        date = datetime.now().strftime("%Y-%m-%d")
        retro_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        plus_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        for route in self.routes:
            if "_A_" in route.name:
                params = {"$filter": f"dueDate ge {date} and dueDate le {plus_date}"}
            else:
                params = {"$filter": f"date ge {retro_date} and date le {date}"}

            try:
                response = requests.get(
                    route.value,
                    headers={"ApiToken": self.api_token},
                    params=params,
                    timeout=timeout
                )
            except requests.exceptions.Timeout:
                response = self.retry_requests(route.value, params, timeout)

            if response.status_code == 401:
                raise NiboAuthError(f"Token Expirado/Inválido: {route.name}")

            data.extend(map_items(route, response.json()))

        return data

    def retry_requests(self, route, params, timeout):
        """Reprocessa uma unica rota apos timeout, com backoff crescente.

        Args:
            route: URL da rota (NiboRoutes.<X>.value).
            params: query params da requisicao (mesmo filtro de data da tentativa original).
            timeout: timeout em segundos, repassado a cada nova tentativa.

        Returns:
            A resposta da requisicao assim que uma tentativa tiver sucesso.

        Raises:
            NiboTimeoutError: se todas as MAX_TRY tentativas esgotarem por timeout.
        """
        for trying in range(1, MAX_TRY + 1):
            try:
                response = requests.get(
                  route,
                  headers={"ApiToken": self.api_token},
                  params=params,
                  timeout=timeout
                )
                return response
            except requests.exceptions.Timeout as error:
                if trying == MAX_TRY:
                    raise NiboTimeoutError(f"error: Maximum trying expection {error}")
                time.sleep(2 * trying)