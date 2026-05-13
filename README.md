# PomodoroHub

## Visão Geral

PomodoroHub é uma API FastAPI que gerencia sessões de Pomodoro com login de usuário.
O frontend é uma interface desktop em PySide6 que consulta o backend e exibe um overlay de presença.

O projeto está preparado para rodar o backend em uma máquina separada e o cliente em outros PCs.

## Estrutura principal

- `main.py` - entrypoint para iniciar o backend com Uvicorn
- `app/app.py` - definição da aplicação FastAPI e lifespan para criar banco
- `desktop_app.py` - cliente desktop PySide6
- `run_server.sh` - script de inicialização do servidor
- `run_client.sh` - script de inicialização do cliente apontando para o servidor
- `requirements.txt` - dependências do projeto

## Instalação

1. Crie e ative o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

## Rodando o backend em uma máquina separada

No servidor dedicado, execute:

```bash
./run_server.sh
```

Isso expõe a API na porta `8000` em todas as interfaces (`0.0.0.0`).

### Acessando pelo cliente

No PC de cada usuário, rode:

```bash
./run_client.sh http://<IP-do-servidor>:8000
```

ou configure a variável de ambiente:

```bash
export POMODORO_HUB_API_URL="http://<IP-do-servidor>:8000"
./run_client.sh
```

## Observações

- O backend deve estar acessível na rede pelo IP do servidor.
- O cliente usa `POMODORO_HUB_API_URL` ou o argumento `--api-url` para se conectar.
- Cada usuário pode iniciar/encerrar Pomodoro e ver no overlay quem está em sessão ativa.

## Endpoints principais

- `POST /users/register`
- `POST /users/login`
- `POST /pomodoro/start`
- `POST /pomodoro/stop`
- `GET /pomodoro/active`
