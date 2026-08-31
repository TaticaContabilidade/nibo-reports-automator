import logging
from src.nibo_client import RouteRequest
from src.config import CLIENTES
from typing import Any
from logs.authentication_logs import NiboAuthError 
from src.userful.generating_documents import generate_reports

def main():
  data_client: list[dict[str, Any]] = []

  for client in CLIENTES:
    try:
      data_client = RouteRequest(client).routes_requests()
      generate_reports(data_client, client)
    except NiboAuthError as error:
      logging.error(f"Erro na autenticacao ({client}): {error}")
      continue

    # TODO: send the generated report PDFs to clients via WhatsApp/email
  
if __name__=='__main__':
  main()