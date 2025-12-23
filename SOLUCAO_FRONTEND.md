# 🚨 Solução Rápida: Frontend não conecta com API

## Problema Identificado

O frontend está carregando a interface, mas provavelmente não está conseguindo conectar com a API porque a variável de ambiente `VITE_API_BASE_URL` não está configurada ou está incorreta.

## ✅ Solução Passo a Passo

### 1. Verificar Variável de Ambiente no Render

1. Acesse o **Render Dashboard**
2. Vá no **Static Site** `voxen-frontend`
3. Clique em **Settings** → **Environment Variables**
4. Verifique se existe:
   ```
   VITE_API_BASE_URL=https://voxen-pi4v.onrender.com/api/v1
   ```

### 2. Se não existir, adicione:

1. Clique em **Add Environment Variable**
2. **Key**: `VITE_API_BASE_URL`
3. **Value**: `https://voxen-pi4v.onrender.com/api/v1`
   ⚠️ **IMPORTANTE**: Substitua `voxen-pi4v.onrender.com` pela URL real do seu backend
4. Clique em **Save Changes**

### 3. Fazer Rebuild (OBRIGATÓRIO)

⚠️ **CRÍTICO**: Após adicionar/alterar variáveis de ambiente, você DEVE fazer um novo deploy:

1. No Render, vá no Static Site
2. Clique em **Manual Deploy** → **Deploy latest commit**
3. Aguarde o build terminar (pode levar alguns minutos)

### 4. Verificar no Console do Navegador

1. Acesse: `https://voxen-frontend.onrender.com/login`
2. Pressione `F12` para abrir o DevTools
3. Vá na aba **Console**
4. Procure por:
   ```
   🔧 API_BASE_URL: https://voxen-pi4v.onrender.com/api/v1
   ```

**Se aparecer `http://localhost:5000/api/v1`**, significa que a variável não foi configurada corretamente.

### 5. Testar Login

1. Tente fazer login com: `admin` / `admin123`
2. Se der erro, verifique no console qual é a mensagem de erro
3. Verifique na aba **Network** se a requisição está sendo feita para a URL correta

## 🔧 Verificar Backend

Certifique-se de que o backend está funcionando:

1. Acesse: `https://voxen-pi4v.onrender.com/health`
   - Deve retornar: `{"status": "ok"}`

2. Acesse: `https://voxen-pi4v.onrender.com/api/v1/test`
   - Deve retornar: `{"success": true, "message": "API está funcionando!"}`

## 🐛 Erros Comuns

### Erro: "Failed to fetch"
- **Causa**: Backend não está acessível ou URL incorreta
- **Solução**: Verifique se a URL do backend está correta e se o backend está rodando

### Erro: "CORS policy"
- **Causa**: Backend não permite requisições do frontend
- **Solução**: O CORS já está configurado para permitir todas as origens (`*`). Se quiser restringir, edite `app/__init__.py`

### Erro: "401 Unauthorized"
- **Causa**: Credenciais incorretas ou usuário não existe
- **Solução**: Verifique se o usuário admin existe no banco de dados

## 📋 Checklist Final

- [ ] Variável `VITE_API_BASE_URL` configurada no Render
- [ ] Rebuild feito após configurar a variável
- [ ] Console mostra URL correta da API
- [ ] Backend está acessível (`/health` retorna OK)
- [ ] Login funciona com credenciais corretas

