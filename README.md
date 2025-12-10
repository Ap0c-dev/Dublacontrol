# Sistema de Controle de Dublagem

Sistema Flask para cadastro e gerenciamento de professores de dublagem e teatro.

## Instalação

1. Crie e ative o ambiente virtual:
```bash
# Criar ambiente virtual (já criado)
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Execute a aplicação:
```bash
python app.py
```

**Nota**: Certifique-se de que o ambiente virtual está ativado antes de executar a aplicação.

A aplicação estará disponível em: `http://localhost:5000`

## Funcionalidades

### Cadastro de Professores

- **URL**: `/cadastro-professores`
- Permite cadastrar múltiplos professores de uma vez
- Campos:
  - **Nome** (obrigatório)
  - **Telefone** (opcional)
  - **Professor de Dublagem** (checkbox - obrigatório selecionar pelo menos um tipo)
  - **Professor de Teatro** (checkbox - obrigatório selecionar pelo menos um tipo)

### Listar Professores

- **URL**: `/professores`
- Exibe todos os professores cadastrados em formato de tabela

## Estrutura do Projeto

```
controle-dublagem/
├── app/
│   ├── __init__.py          # Inicialização da aplicação Flask
│   ├── models/
│   │   └── professor.py     # Modelo de dados Professor
│   └── routes.py            # Rotas da aplicação
├── templates/
│   ├── base.html            # Template base
│   ├── cadastro_professores.html  # Formulário de cadastro
│   └── listar_professores.html    # Lista de professores
├── app.py                   # Arquivo principal
├── config.py                # Configurações
└── requirements.txt         # Dependências Python
```

## Banco de Dados

O sistema utiliza SQLite por padrão. O arquivo `controle_dublagem.db` será criado automaticamente na primeira execução.

Para usar outro banco de dados, altere a variável `SQLALCHEMY_DATABASE_URI` no arquivo `config.py`.

