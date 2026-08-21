import logging
from src.nibo_client import RouteRequest
from src.config import CLIENTES
from typing import Any
from logs.authentication_logs import NiboAuthError 

def main():
  data_client: list[dict[str, Any]] = []

  for client in CLIENTES:
    try:
      data_client = RouteRequest(client)
      print(data_client.routes_requests())
    except NiboAuthError as error:
      logging.error(f"Erro na autenticacao ({client}): {error}")
      continue

    # Fazer o mapping dos dados
    # chamar a classe que irá criar o pdf
    # enviar para os clientes
  
if __name__=='__main__':
  main()