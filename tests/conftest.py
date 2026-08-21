import os

# IMPORTANT: this must be set BEFORE any test imports src.config or
# src.nibo_client, because config.py reads os.environ at module level
# (the first time it's imported). conftest.py is loaded by pytest
# before test module collection, which guarantees the right order.
os.environ.setdefault("NIBO_KEY_EVA_CLINICA", "token-fake-eva-clinica")
os.environ.setdefault("NIBO_KEY_DR_MIKLE", "token-fake-dr-mikle")
