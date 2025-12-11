# Configuração do Banco de Dados no Render

## ⚠️ IMPORTANTE: Erro "unable to open database file"

Se você está vendo este erro no Render, significa que a variável `DATABASE_URL` não está configurada.

## Solução: Configurar PostgreSQL no Render

### Passo 1: Criar Banco PostgreSQL

1. No painel do Render, clique em **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `dublacontrol-db` (ou o nome que preferir)
   - **Database**: `dublacontrol` (ou o nome que preferir)
   - **User**: Será gerado automaticamente
   - **Region**: Escolha a mesma região do seu Web Service
3. Clique em **"Create Database"**

### Passo 2: Copiar DATABASE_URL

1. Após criar o banco, vá até a página do banco
2. Na seção **"Connections"**, copie a **"Internal Database URL"**
3. Exemplo: `postgres://user:password@host:5432/database`

### Passo 3: Adicionar ao Web Service

1. Vá até seu **Web Service** no Render
2. Clique em **"Environment"**
3. Clique em **"Add Environment Variable"**
4. Adicione:
   - **Key**: `DATABASE_URL`
   - **Value**: Cole a URL que você copiou
5. Clique em **"Save Changes"**

### Passo 4: Fazer Deploy

1. O Render fará deploy automático, ou
2. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

## Verificação

Após o deploy, verifique os logs. Você deve ver:
```
✓ Ambiente: PRD
✓ Banco de dados: postgresql://...
✓ Tabelas criadas/verificadas com sucesso
```

## ⚠️ Sem DATABASE_URL

Se não configurar `DATABASE_URL`, a aplicação tentará usar SQLite temporário:
- ✅ Funciona, mas...
- ⚠️ Dados serão perdidos quando o serviço reiniciar
- ⚠️ Não recomendado para produção

## Troubleshooting

### Erro: "unable to open database file"
- **Causa**: `DATABASE_URL` não configurado
- **Solução**: Configure PostgreSQL conforme acima

### Erro: "connection refused"
- **Causa**: URL do banco incorreta ou banco inativo
- **Solução**: Verifique se o banco está ativo e a URL está correta

### Erro: "relation does not exist"
- **Causa**: Tabelas não foram criadas
- **Solução**: A aplicação cria automaticamente na primeira requisição. Aguarde alguns segundos.

