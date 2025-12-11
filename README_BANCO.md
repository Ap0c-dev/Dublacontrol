# Configuração de Bancos de Dados

Este projeto suporta dois ambientes separados: **desenvolvimento (dev)** e **produção (prd)**.

## Como Funciona

### Desenvolvimento (Local)
Por padrão, quando você roda a aplicação localmente, ela usa o banco de dados de **desenvolvimento**:
- **Arquivo**: `/home/tiago/banco_lucy_dev`
- **Ambiente**: `dev` (padrão)

### Produção
Para usar o banco de produção, você precisa definir a variável de ambiente `ENVIRONMENT=prd`:
- **Arquivo**: `/home/tiago/banco_lucy_prd`
- **Ambiente**: `prd`

## Como Usar

### Rodar em Desenvolvimento (Padrão)
```bash
# Apenas rode normalmente - usa dev automaticamente
python wsgi.py
# ou
flask run
```

### Rodar em Produção (Local)
```bash
# Defina a variável de ambiente antes de rodar
export ENVIRONMENT=prd
python wsgi.py
```

### No Render (Produção)
No Render, a aplicação detecta automaticamente o ambiente de produção através da variável `DATABASE_URL` (PostgreSQL).

## Variáveis de Ambiente

- `ENVIRONMENT`: Define o ambiente (`dev` ou `prd`)
  - Se não definida, usa `dev` por padrão
  - Se `DATABASE_URL` estiver definida, força `prd`

- `DATABASE_PATH`: Define o diretório base para os bancos SQLite
  - Padrão: `/home/tiago`
  - Os arquivos serão: `{DATABASE_PATH}/banco_lucy_dev` e `{DATABASE_PATH}/banco_lucy_prd`

- `DATABASE_URL`: URL do banco de dados (PostgreSQL no Render)
  - Quando definida, força ambiente de produção

## Scripts

### Corrigir Banco de Dados
```bash
# Corrigir banco de desenvolvimento (padrão)
python fix_database.py

# Corrigir banco de produção
export ENVIRONMENT=prd
python fix_database.py
```

## Estrutura dos Arquivos

```
/home/tiago/
├── banco_lucy_dev    # Banco de desenvolvimento
└── banco_lucy_prd    # Banco de produção
```

## Importante

⚠️ **Atenção**: Os bancos de dev e prd são completamente separados. Dados cadastrados em um não aparecem no outro.

