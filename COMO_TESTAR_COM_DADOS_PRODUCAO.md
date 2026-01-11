# Como Testar Localmente com Dados de Produção

Este guia explica como conectar sua aplicação local ao banco de dados de produção para testar com dados reais.

## ⚠️ AVISOS IMPORTANTES

1. **CUIDADO**: Você estará trabalhando com dados reais de produção!
2. **NÃO FAÇA ALTERAÇÕES**: Use apenas para leitura/testes
3. **BACKUP**: Sempre faça backup antes de qualquer operação
4. **RECOMENDAÇÃO**: Prefira usar uma cópia do banco de produção quando possível

## 🎯 Opções Disponíveis

### Opção 1: Conectar ao PostgreSQL de Produção (Render) ⚠️ NÃO RECOMENDADO

**Use apenas se necessário e com muito cuidado!**

#### Passos:

1. **Obter a URL do banco de produção**

   - Acesse o painel do Render
   - Vá em "Dashboard" > Seu serviço > "Environment"
   - Copie o valor de `DATABASE_URL`
   - Formato: `postgres://usuario:senha@host:porta/database`

2. **Criar arquivo `.env` na raiz do projeto**

   ```bash
   cd /home/tiago/controle-dublagem
   ```

   Crie o arquivo `.env`:
   ```bash
   # .env
   DATABASE_URL=postgres://usuario:senha@host:porta/database
   ENVIRONMENT=prd
   SECRET_KEY=sua-chave-local
   ```

3. **Instalar dependências do PostgreSQL (se necessário)**

   ```bash
   # Já deve estar instalado via requirements.txt
   pip install psycopg2-binary
   ```

4. **Iniciar o servidor**

   ```bash
   source venv/bin/activate
   python wsgi.py
   ```

5. **Testar**

   - Acesse: http://localhost:8080
   - Faça login com credenciais de produção
   - **CUIDADO**: Qualquer alteração será feita no banco de produção!

---

### Opção 2: Usar Banco SQLite Local de Produção ✅ RECOMENDADO

Esta opção usa uma cópia local do banco de produção (se você já tiver feito backup).

#### Passos:

1. **Verificar se existe banco de produção local**

   ```bash
   ls -lh /home/tiago/banco_lucy_prd
   ```

2. **Se não existir, fazer backup do banco de produção**

   Se você tem acesso ao banco de produção via Render, pode fazer um dump:

   ```bash
   # Conectar ao PostgreSQL e fazer dump
   pg_dump -h host -U usuario -d database > backup_producao.sql
   ```

   Ou se você já tem um backup SQLite, copie para o local correto.

3. **Configurar para usar banco de produção local**

   Crie um arquivo `.env` na raiz do projeto:

   ```bash
   # .env
   ENVIRONMENT=prd
   DATABASE_PATH=/home/tiago
   SECRET_KEY=sua-chave-local
   ```

   Isso fará o sistema usar `/home/tiago/banco_lucy_prd` (banco SQLite local de produção).

4. **Iniciar o servidor**

   ```bash
   source venv/bin/activate
   python wsgi.py
   ```

5. **Verificar qual banco está sendo usado**

   Os logs devem mostrar algo como:
   ```
   Usando banco: sqlite:////home/tiago/banco_lucy_prd
   ```

---

### Opção 3: Fazer Backup e Restaurar Localmente ✅ MAIS SEGURO

Esta é a opção mais segura: fazer um backup do banco de produção e restaurar localmente.

#### Passo 1: Fazer Backup do Banco de Produção

**Se estiver usando PostgreSQL no Render:**

```bash
# Instalar PostgreSQL client (se não tiver)
sudo apt-get install postgresql-client

# Fazer dump do banco
pg_dump -h <HOST> -U <USUARIO> -d <DATABASE> > backup_producao_$(date +%Y%m%d).sql

# Ou se tiver acesso via DATABASE_URL:
pg_dump $DATABASE_URL > backup_producao_$(date +%Y%m%d).sql
```

**Se estiver usando SQLite:**

```bash
# Copiar o arquivo do banco
cp /caminho/para/banco_producao.db /home/tiago/banco_lucy_prd
```

#### Passo 2: Restaurar Localmente

**Para PostgreSQL:**

```bash
# Criar banco local (se necessário)
createdb controle_dublagem_local

# Restaurar
psql controle_dublagem_local < backup_producao_YYYYMMDD.sql
```

**Para SQLite:**

```bash
# Já está copiado, apenas use
cp backup_producao.db /home/tiago/banco_lucy_prd
```

#### Passo 3: Configurar e Rodar

```bash
# .env
ENVIRONMENT=prd
DATABASE_PATH=/home/tiago
# Ou se usar PostgreSQL local:
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/controle_dublagem_local
```

---

## 🔍 Verificar Qual Banco Está Sendo Usado

Execute este comando para ver qual banco está configurado:

```bash
python -c "from app import create_app; app = create_app(); print('Banco:', app.config.get('SQLALCHEMY_DATABASE_URI'))"
```

Ou veja os logs ao iniciar o servidor - eles mostram qual banco está sendo usado.

## 📋 Resumo das Opções

| Opção | Segurança | Complexidade | Recomendação |
|-------|-----------|-------------|--------------|
| Conectar direto ao PostgreSQL | ⚠️ Baixa | Média | ❌ Não recomendado |
| Usar SQLite local (prd) | ✅ Média | Baixa | ✅ Recomendado |
| Backup e restaurar | ✅ Alta | Alta | ✅✅ Mais seguro |

## 🎯 Recomendação Final

**Para testar com dados de produção localmente:**

1. Use a **Opção 3** (Backup e Restaurar) se possível
2. Se já tiver um banco SQLite de produção local, use a **Opção 2**
3. **NUNCA** use a Opção 1 (conectar direto) a menos que seja absolutamente necessário e você tenha certeza do que está fazendo

## 🚀 Testando o Dashboard com Dados Reais

Após configurar:

1. Inicie o backend: `python wsgi.py`
2. Inicie o frontend: `cd frontend_lovable/connect-dashboard-main && npm run dev`
3. Acesse: http://localhost:8080
4. Faça login com credenciais válidas
5. Teste as tabs do Dashboard:
   - **Professores**: Deve mostrar professores reais com métricas reais
   - **Alunos**: Deve mostrar dados reais de alunos
   - **Receita**: Deve mostrar receita real

## 🔄 Sincronizar Dados (Opcional)

Se quiser manter os dados sincronizados:

1. Faça backup periódico do banco de produção
2. Restaure localmente quando necessário
3. Use scripts de sincronização (se criar)

## ⚠️ Lembrete Final

- **SEMPRE** faça backup antes de qualquer operação
- **NUNCA** faça alterações no banco de produção sem necessidade
- **USE** ambiente de desenvolvimento para testes quando possível
- **TESTE** localmente antes de fazer deploy


