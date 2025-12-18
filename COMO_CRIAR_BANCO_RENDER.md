# Como Criar um Banco PostgreSQL no Render

## 📋 Passo a Passo Completo

### 1. Acessar o Render

1. Acesse https://render.com
2. Faça login na sua conta (ou crie uma conta gratuita se ainda não tiver)

### 2. Criar Novo Banco de Dados

1. No dashboard do Render, clique no botão **"New +"** (canto superior direito)
2. Selecione **"PostgreSQL"** na lista de opções

### 3. Configurar o Banco

Preencha os campos do formulário:

#### Informações Básicas

- **Name**: Dê um nome para seu banco (ex: `controle-dublagem-db`)
- **Database**: Nome do banco de dados (ex: `controle_dublagem`)
  - Pode deixar o padrão ou escolher um nome personalizado
- **User**: Nome do usuário do banco (ex: `controle_user`)
  - Pode deixar o padrão ou escolher um nome personalizado
- **Region**: Escolha a região mais próxima do Brasil
  - Recomendado: **Oregon (US West)** ou **Frankfurt (EU Central)**
  - Regiões mais próximas = menor latência

#### Plano e Recursos

- **Plan**: Escolha o plano
  - **Free**: Gratuito (1 GB, pode ser pausado)
  - **Starter**: ~$7/mês (1 GB RAM, 10 GB storage, sem pausas)
  - **Standard**: ~$25/mês (mais recursos)

**Para começar, escolha "Free"** se quiser testar sem custos.

#### Configurações Avançadas (Opcional)

- **PostgreSQL Version**: Deixe a versão mais recente (recomendado)
- **Databases**: Pode deixar o padrão (1 database)
- **Extensions**: Não precisa configurar agora

### 4. Criar o Banco

1. Clique no botão **"Create Database"**
2. Aguarde alguns minutos enquanto o Render cria o banco
3. Você verá uma tela de "Creating..." com progresso

### 5. Obter a Connection String (DATABASE_URL)

Após o banco ser criado:

1. Clique no banco de dados criado no dashboard
2. Na página do banco, procure pela seção **"Connection"** ou **"Connections"**
3. Você verá a **"Internal Database URL"** ou **"External Database URL"**

**Formato da URL:**
```
postgres://usuario:senha@host:porta/database
```

**Exemplo:**
```
postgres://controle_user:abc123xyz@dpg-xxxxx-a.oregon-postgres.render.com/controle_dublagem
```

### 6. Configurar no Seu Web Service

Agora você precisa adicionar essa URL como variável de ambiente no seu Web Service:

#### Opção A: Render detecta automaticamente (Recomendado)

Se você criou o banco **antes** de criar o Web Service:
1. Ao criar o Web Service, o Render pode detectar automaticamente
2. Selecione o banco na lista de "PostgreSQL Databases"

#### Opção B: Adicionar manualmente

1. Vá para o seu **Web Service** no dashboard do Render
2. Clique em **"Environment"** no menu lateral
3. Clique em **"Add Environment Variable"**
4. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: Cole a URL completa do banco (a que você copiou)
5. Clique em **"Save Changes"**

### 7. Verificar se Está Funcionando

1. Faça um deploy do seu Web Service (ou aguarde o auto-deploy)
2. Verifique os logs do Web Service
3. Procure por mensagens como:
   - ✅ "✓ Banco de dados: postgresql://..."
   - ✅ "✓ Tabelas criadas/verificadas com sucesso"

Se aparecer erro de conexão, verifique:
- Se a `DATABASE_URL` está correta
- Se o banco está ativo (não pausado)
- Se o formato da URL está correto

---

## 🔍 Como Encontrar a DATABASE_URL no Render

### Método 1: Página do Banco

1. Clique no banco PostgreSQL no dashboard
2. Role até a seção **"Connections"**
3. Você verá:
   - **Internal Database URL** (para serviços no mesmo Render)
   - **External Database URL** (para conexões externas)

**Use a Internal Database URL** se seu Web Service também está no Render.

### Método 2: Variável de Ambiente Automática

O Render pode criar automaticamente uma variável chamada:
- `DATABASE_URL` (se você conectou o banco ao Web Service)

Verifique em: **Web Service → Environment**

### Método 3: Connection String Manual

Se precisar montar manualmente:
```
postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
```

Onde:
- `[USER]`: Nome do usuário (ex: `controle_user`)
- `[PASSWORD]`: Senha (gerada automaticamente pelo Render)
- `[HOST]`: Host do banco (ex: `dpg-xxxxx-a.oregon-postgres.render.com`)
- `[PORT]`: Porta (geralmente `5432`)
- `[DATABASE]`: Nome do banco (ex: `controle_dublagem`)

---

## ⚠️ Importante: Formato da URL

O Render fornece URLs no formato `postgres://`, mas o SQLAlchemy precisa de `postgresql://`.

**Boa notícia:** Seu sistema já faz essa conversão automaticamente no `config.py`!

Mas se precisar corrigir manualmente:
```
# Formato do Render
postgres://usuario:senha@host:porta/database

# Formato necessário
postgresql://usuario:senha@host:porta/database
```

---

## 🔐 Segurança

### Senha do Banco

- O Render gera uma senha automaticamente
- A senha está na URL de conexão
- **NÃO compartilhe** a URL publicamente
- Mantenha a `DATABASE_URL` como variável de ambiente (não no código)

### Acesso ao Banco

- **Internal URL**: Só funciona entre serviços do Render
- **External URL**: Funciona de qualquer lugar (mais flexível, mas menos seguro)
- Para produção, use **Internal URL** se possível

---

## 📊 Verificar Status do Banco

No dashboard do Render, você pode ver:

1. **Status**: Running, Paused, etc.
2. **Storage**: Quanto espaço está usando
3. **Connections**: Conexões ativas
4. **Logs**: Logs do banco de dados

### Banco Pausado (Plano Gratuito)

No plano gratuito, o banco pode ser **pausado** após inatividade:
- Primeira conexão após pausa pode demorar alguns segundos
- Dados não são perdidos
- Para evitar pausas, use um plano pago

---

## 🛠️ Troubleshooting

### Erro: "could not connect to server"

**Soluções:**
1. Verifique se o banco está **Running** (não pausado)
2. Verifique se a `DATABASE_URL` está correta
3. Verifique se está usando `postgresql://` (não `postgres://`)
4. Aguarde alguns segundos se o banco estava pausado

### Erro: "password authentication failed"

**Soluções:**
1. Copie a URL novamente do dashboard do Render
2. Verifique se não há espaços extras na URL
3. Verifique se a senha na URL está correta

### Erro: "database does not exist"

**Soluções:**
1. Verifique o nome do banco na URL
2. Verifique se o banco foi criado corretamente
3. Tente recriar o banco se necessário

### Banco está pausado

**No plano gratuito:**
- O banco pode pausar após inatividade
- Clique em "Resume" no dashboard
- Ou faça uma conexão (ele acorda automaticamente)

---

## 📝 Checklist Completo

- [ ] Criar conta no Render (se não tiver)
- [ ] Criar novo banco PostgreSQL
- [ ] Escolher nome e região
- [ ] Escolher plano (Free para começar)
- [ ] Aguardar criação do banco
- [ ] Copiar a DATABASE_URL
- [ ] Adicionar DATABASE_URL no Web Service
- [ ] Verificar logs para confirmar conexão
- [ ] Testar a aplicação

---

## 🎯 Resumo Rápido

1. **Render Dashboard** → "New +" → "PostgreSQL"
2. **Configurar**: Nome, região, plano
3. **Criar** e aguardar
4. **Copiar** a DATABASE_URL
5. **Adicionar** no Web Service como variável de ambiente
6. **Pronto!** Seu sistema usará PostgreSQL automaticamente

---

## 💡 Dicas

- **Comece com o plano Free** para testar
- **Use Internal Database URL** se possível (mais seguro)
- **Mantenha a URL segura** (não commite no Git)
- **Monitore o uso** no dashboard do Render
- **Faça backups** regularmente (Render tem backups automáticos em planos pagos)

---

## 🔄 Próximos Passos

Após criar o banco:

1. ✅ Configure a `DATABASE_URL` no Web Service
2. ✅ Faça deploy da aplicação
3. ✅ Verifique os logs para confirmar conexão
4. ✅ Teste criar/editar dados
5. ✅ Configure backups (se necessário)

**Pronto! Seu sistema agora está usando PostgreSQL no Render!** 🎉








