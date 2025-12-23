# 🔍 Verificar Deploy do Frontend

## ⚠️ Problema: Site carregando mas não funcionando

Se o site está carregando a interface mas não consegue fazer login ou conectar com a API, verifique:

## ✅ Checklist de Verificação

### 1. Variável de Ambiente `VITE_API_BASE_URL`

**No Render Static Site**, vá em **Settings** → **Environment Variables** e verifique:

```
VITE_API_BASE_URL=https://voxen-pi4v.onrender.com/api/v1
```

⚠️ **IMPORTANTE**:
- A URL deve ser a do **backend** (não do frontend)
- Deve incluir `/api/v1` no final
- Deve usar `https://` (não `http://`)
- Não deve ter barra `/` no final

### 2. Verificar no Console do Navegador

1. Abra o site: `https://voxen-frontend.onrender.com/login`
2. Pressione `F12` para abrir o DevTools
3. Vá na aba **Console**
4. Procure por estas mensagens:
   ```
   🔧 API_BASE_URL: ...
   🔧 VITE_API_BASE_URL: ...
   ```

**Se aparecer:**
- `API_BASE_URL: http://localhost:5000/api/v1` → ❌ Variável de ambiente não configurada
- `API_BASE_URL: https://SEU_BACKEND.onrender.com/api/v1` → ✅ Configurado corretamente

### 3. Verificar Erros de CORS

No console do navegador, procure por erros como:
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Solução**: Verificar se o CORS está configurado no backend para permitir o domínio do frontend.

### 4. Verificar Erros de Rede

No console, vá na aba **Network** e tente fazer login. Verifique:
- Se a requisição para `/api/v1/auth/login` está sendo feita
- Qual é o status da resposta (200, 401, 500, etc.)
- Se há erro de conexão

### 5. Rebuild após Alterar Variáveis de Ambiente

⚠️ **IMPORTANTE**: Após alterar variáveis de ambiente no Render, você precisa fazer um **novo deploy**:

1. No Render, vá no Static Site
2. Clique em **Manual Deploy** → **Deploy latest commit**
3. Ou faça um commit vazio para forçar rebuild:
   ```bash
   git commit --allow-empty -m "trigger rebuild"
   git push
   ```

## 🔧 Solução Rápida

### Passo 1: Verificar/Configurar Variável de Ambiente

No Render Static Site:
1. Vá em **Settings** → **Environment Variables**
2. Adicione ou edite:
   ```
   VITE_API_BASE_URL=https://SEU_BACKEND.onrender.com/api/v1
   ```
   (Substitua `SEU_BACKEND` pela URL real do seu backend)

### Passo 2: Fazer Rebuild

1. No Render, vá no Static Site
2. Clique em **Manual Deploy** → **Deploy latest commit**
3. Aguarde o build terminar

### Passo 3: Testar

1. Acesse: `https://voxen-frontend.onrender.com/login`
2. Abra o console (F12)
3. Verifique se `API_BASE_URL` está correto
4. Tente fazer login com as credenciais que você configurou

## 🐛 Troubleshooting

### Erro: "Failed to fetch" ou "Network error"

**Causa**: Backend não está acessível ou CORS bloqueado

**Solução**:
1. Verifique se o backend está rodando: `https://SEU_BACKEND.onrender.com/health`
2. Verifique se o CORS está configurado no backend

### Erro: "401 Unauthorized"

**Causa**: Credenciais incorretas ou backend não autenticando

**Solução**:
1. Verifique se o usuário admin existe no banco
2. Tente criar o admin via script ou interface

### Erro: "CORS policy"

**Causa**: Backend não permite requisições do frontend

**Solução**: No backend (`app/__init__.py`), verifique se o CORS está configurado para permitir o domínio do frontend.

