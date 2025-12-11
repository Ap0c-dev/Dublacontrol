# Informação sobre os Bancos de Dados

## Bancos Disponíveis

### 1. Banco Antigo (Legado)
- **Caminho**: `/home/tiago/banco_lucy`
- **Uso**: Banco antigo, não é mais usado pela aplicação
- **Status**: Mantido apenas para referência/migração

### 2. Banco de Desenvolvimento (DEV)
- **Caminho**: `/home/tiago/banco_lucy_dev`
- **Uso**: Banco usado quando você roda a aplicação localmente (padrão)
- **Como usar**: Apenas rode a aplicação normalmente
- **Comando**: `python wsgi.py` ou `flask run`

### 3. Banco de Produção (PRD)
- **Caminho**: `/home/tiago/banco_lucy_prd`
- **Uso**: Banco usado quando você define `ENVIRONMENT=prd`
- **Como usar**: `export ENVIRONMENT=prd && python wsgi.py`

### 4. Banco no Render (Produção)
- **Tipo**: PostgreSQL
- **Configuração**: Automática via variável `DATABASE_URL`
- **Uso**: Aplicação em produção no Render

## Qual Banco Está Sendo Usado?

### Localmente (Desenvolvimento)
Por padrão, quando você roda localmente, a aplicação usa:
- **Banco**: `/home/tiago/banco_lucy_dev`
- **Arquivo**: `banco_lucy_dev`

### Para Verificar Qual Banco Está Sendo Usado

Execute no terminal:
```bash
python -c "from app import create_app; app = create_app(); print(app.config.get('SQLALCHEMY_DATABASE_URI'))"
```

Ou veja os logs ao iniciar a aplicação - eles mostram qual banco está sendo usado.

## Importante ⚠️

- **banco_lucy** (antigo) - NÃO é mais usado pela aplicação
- **banco_lucy_dev** - Usado localmente (padrão)
- **banco_lucy_prd** - Usado quando `ENVIRONMENT=prd`
- **PostgreSQL no Render** - Usado em produção no Render

Se você está visualizando o banco antigo (`banco_lucy`) no SQLite Browser, os dados não aparecerão porque a aplicação está salvando em `banco_lucy_dev`.

## Como Visualizar o Banco Correto

No SQLite Browser, abra o arquivo:
- **Desenvolvimento**: `/home/tiago/banco_lucy_dev`
- **Produção local**: `/home/tiago/banco_lucy_prd`

