# 🚀 Deploy do Frontend Voxen

## ⚠️ Problema: Interface Antiga Aparecendo

Se você está vendo a interface antiga (templates HTML do Flask), significa que está acessando o **backend** diretamente. O frontend React precisa ser configurado separadamente.

## ✅ Solução: Configurar Frontend como Static Site no Render

### Opção 1: Static Site Separado (Recomendado)

1. **No Render Dashboard**, clique em **New +** → **Static Site**

2. **Conecte seu repositório GitHub** (o mesmo repositório do backend)

3. **Configure o Static Site:**
   - **Name**: `voxen-frontend`
   - **Root Directory**: `frontend_lovable/connect-dashboard-main`
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**: `dist`

4. **Environment Variables** (adicionar):
   ```
   VITE_API_BASE_URL=https://voxen-pi4v.onrender.com/api/v1
   ```
   ⚠️ **IMPORTANTE**: Substitua `voxen-pi4v.onrender.com` pela URL real do seu backend

5. **Clique em "Create Static Site"**

6. Após o deploy, você terá uma URL como: `https://voxen-frontend.onrender.com`

7. **Acesse o frontend pela URL do Static Site**, não pela URL do backend!

### Opção 2: Servir Frontend pelo Backend (Alternativa)

Se preferir servir tudo pelo mesmo domínio, você pode configurar o backend para servir os arquivos estáticos do frontend buildado.

**Passos:**
1. Fazer build do frontend localmente:
   ```bash
   cd frontend_lovable/connect-dashboard-main
   npm install
   npm run build
   ```

2. Copiar a pasta `dist` para o backend:
   ```bash
   cp -r frontend_lovable/connect-dashboard-main/dist static/frontend
   ```

3. Adicionar rota no backend para servir o frontend (já implementado abaixo)

## 🔧 Verificar Configuração Atual

### Backend (voxen-pi4v.onrender.com)
- ✅ Serve a API REST em `/api/v1/*`
- ✅ Serve templates HTML antigos em `/`, `/login`, etc.
- ❌ **NÃO serve o frontend React**

### Frontend (precisa ser criado)
- ⚠️ **Ainda não configurado como Static Site**
- ⚠️ Precisa ser acessado pela URL do Static Site, não pela URL do backend

## 📝 Checklist

- [ ] Static Site criado no Render
- [ ] Root Directory configurado: `frontend_lovable/connect-dashboard-main`
- [ ] Build Command: `npm install && npm run build`
- [ ] Publish Directory: `dist`
- [ ] Environment Variable `VITE_API_BASE_URL` configurada com a URL do backend
- [ ] Deploy concluído com sucesso
- [ ] Acessando o frontend pela URL do Static Site (não pela URL do backend)

## 🐛 Troubleshooting

### "Interface antiga aparecendo"
- **Causa**: Acessando o backend diretamente
- **Solução**: Criar Static Site separado e acessar pela URL do Static Site

### "Erro ao fazer build"
- Verifique se o `Root Directory` está correto: `frontend_lovable/connect-dashboard-main`
- Verifique se o `package.json` existe no diretório

### "API não conecta"
- Verifique se `VITE_API_BASE_URL` está configurada corretamente
- Verifique se o backend está rodando e acessível
- Verifique se o CORS está configurado no backend

### "404 ao acessar rotas do frontend"
- O Vite precisa de configuração de `_redirects` ou `vercel.json` para SPA
- No Render Static Site, adicione um arquivo `_redirects` na pasta `public`:
  ```
  /*    /index.html   200
  ```

