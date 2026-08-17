import os
from enum import Enum

# Configuração das chaves API's dos clientes da Tatica

CLIENTES = {
    "eva clinica": os.environ["NIBO_KEY_EVA_CLINICA"],
    "dr mikle": os.environ["NIBO_KEY_DR_MIKLE"]
}

class NiboRoutes(Enum): 
    CONTAS_RECEBIDAS = "https://api.nibo.com.br/empresas/v1/receipts"
    CONTAS_PAGAS = "https://api.nibo.com.br/empresas/v1/payments"
    CONTAS_A_PAGAR = "https://api.nibo.com.br/empresas/v1/schedules/debit/opened"
    CONTAS_A_RECEBER = "https://api.nibo.com.br/empresas/v1/schedules/credit"
