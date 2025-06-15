# Caipyra Ledger

Esta é a implementação de uma ledger (livro razão) simples apenas para demonstração que faz parte do conteúdo
da minha palestra [O que faz uma ledger?](https://talks.python.org.br/caipyra-2025/talk/TFDNJW/).

## Como rodar

Os requisitos para rodar esse projeto localmente são:
* [uv](https://docs.astral.sh/uv), utilizamos ele como gerenciador de dependências/python
* [docker](https://www.docker.com), utilizamos ele para subir uma instância local do PostgreSQL

Após ter essas duas ferramentas instaladas execute o seguinte comando:
```shell
make run-app
```

Esse comando irá instalar/subir todas as dependências necessárias e irá expor a API na porta __8000__, com isso você
poderá acessar as seguintes documentações:
* Swagger: [localhost:8000/docs](http://localhost:8000/docs)
* Redoc: [localhost:8000/redoc](http://localhost:8000/redoc)

Para parar a API execute a combinação _CTRL + C_ no terminal e logo após execute o seguinte comando:
```shell
make stop-local
```
