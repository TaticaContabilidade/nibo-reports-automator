# nibo-reports-automator

Automatiza a extração de relatórios de contas (a pagar, a receber, pagas e
recebidas) da API oficial do NIBO, gera um PDF por tipo de conta e por
cliente, e envia todos os relatórios da semana num único e-mail.

Documentação de requisitos, arquitetura e backlog completo em
[`docs/06_Requisitos_e_Backlog.md`](docs/06_Requisitos_e_Backlog.md).

## Estrutura do projeto

```
src/
├── config.py                    # clientes (chave NIBO por empresa) e rotas da API
├── main.py                      # ponto de entrada: roda o fluxo pra cada cliente
├── nibo_client.py                # autenticação + requisições às 4 rotas do NIBO
├── send_email.py                 # monta e envia o e-mail com os 4 PDFs anexados
├── logger/
│   └── logging_sendemail.py      # classe abstrata Logging, usada por send_email.py
└── userful/
    ├── map_dict.py                # mapeia a resposta bruta da API pros campos do relatório
    └── generating_documents.py    # gera os 4 PDFs (reportlab), um por rota

logs/
└── authentication_logs.py        # exceções (NiboAuthError, NiboTimeoutError)

tests/            # suite pytest (mock das rotas do NIBO via requests-mock)
relatorios/       # saída dos PDFs gerados, por empresa (ignorado no git)
docs/             # requisitos, backlog e documentação de arquitetura
```

`logs/` reúne o que é transversal a toda a aplicação (exceções e logging),
enquanto `src/` é o código específico do fluxo NIBO → relatório → envio.

## Configuração

Crie um `.env` na raiz (nunca comitado — já está no `.gitignore`) com, no
mínimo:

```
NIBO_KEY_EVA_CLINICA=...
NIBO_KEY_SANTOS_E_NOGUEIRA=...

EMAIL_GMAIL=...
GMAIL_APP_PASS=...      # App Password do Gmail (não a senha normal da conta)
SENDER_EMAIL=...
RECEIVER_EMAIL=...
```

Sem espaço nenhum ao redor do `=` — `NOME=valor`, não `NOME = valor`.

Cada cliente novo entra em `CLIENT_ENV_VARS` (`src/config.py`) com o nome da
env var correspondente; ele só é processado se essa variável existir no
ambiente, então dá pra deixar um cliente cadastrado e só "ligar" ele depois,
adicionando a env var.

## Rodando

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . -r requirements-dev.txt   # requirements-dev.txt já inclui requirements.txt

export $(grep -v '^#' .env | xargs)
python -m src.main
```

## Testes

```bash
pytest tests/
```
