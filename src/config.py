import os

# Configuração das chaves API's dos clientes da Tatica

CLIENTES = {
    "eva clinica": os.environ["NIBO_KEY_EVA_CLINICA"],
    "dr mikle": os.environ["NIBO_KEY_DR_MIKLE"]
}

NIBO_ROUTES = {
    "contas_recebidas": "https://api.nibo.com.br/empresas/v1/receipts",
    "contas_pagas": "https://api.nibo.com.br/empresas/v1/payments",
    "contas_a_pagar": "https://api.nibo.com.br/empresas/v1/schedules/debit/opened",
    "contas_a_receber": "https://api.nibo.com.br/empresas/v1/schedules/credit"
}