class NiboAuthError(Exception):
    """Levantada quando a API do NIBO retorna 401 (token invalido/expirado)."""


class NiboTimeoutError(Exception):
    """Levantada quando as tentativas de retry esgotam apos timeouts consecutivos."""
