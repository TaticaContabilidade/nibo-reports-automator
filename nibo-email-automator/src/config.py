import os
from enum import Enum

# Configuração das chaves API's dos clientes da Tatica
#
# A client is only included in CLIENTES once its env var is actually set.
# This lets a not-yet-onboarded company sit here as a placeholder without
# crashing the app on import - just set its env var later to activate it.
CLIENT_ENV_VARS = {
    "eva clinica": "NIBO_KEY_EVA_CLINICA",
    "santos e nogueira": "NIBO_KEY_SANTOS_E_NOGUEIRA",
    "empresa fantasma": "NIBO_KEY_EMPRESA_FANTASMA",  # placeholder client used to test the cost center columns
}

CLIENTES = {
    name: os.environ[env_var]
    for name, env_var in CLIENT_ENV_VARS.items()
    if env_var in os.environ
}

class NiboRoutes(Enum): 
    CONTAS_RECEBIDAS = "https://api.nibo.com.br/empresas/v1/receipts"
    CONTAS_PAGAS = "https://api.nibo.com.br/empresas/v1/payments"
    CONTAS_A_PAGAR = "https://api.nibo.com.br/empresas/v1/schedules/debit/opened"
    CONTAS_A_RECEBER = "https://api.nibo.com.br/empresas/v1/schedules/credit"
