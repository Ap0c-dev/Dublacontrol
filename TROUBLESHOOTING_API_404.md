# 🔍 Troubleshooting: Erro 404 na API

## Problema: `https://voxen-pi4v.onrender.com/api/v1` retorna 404

## ✅ Verificações Passo a Passo

### 1. Verificar se o Backend está Rodando

Acesse a rota de health check:
```
https://voxen-pi4v.onrender.com/health
```

**Resultado esperado:**
```json
{"status": "ok"}
```

**Se retornar 404 ou erro:**
- O backend não está rodando
- Verifique os logs no Render Dashboard
- Verifique se o serviço está "Live" (não "Sleeping")

### 2. Verificar Rota de Teste da API

Acesse:
```
https://voxen-pi4v.onrender.com/api/v1/test
```

**Resultado esperado:**
```json
{"success": true, "message": "API está funcionando!"}
```

**Se retornar 404:**
- O blueprint da API não está registrado
- Verifique os logs do servidor para erros de importação

### 3. Verificar Rota Raiz da API

Acesse:
```
https://voxen-pi4v.onrender.com/api/v1/
```

**Resultado esperado:**
```json
{
  "success": true,
  "message": "API Voxen está funcionando!",
  "version": "1.0",
  "endpoints": {...}
}
```

### 4. Verificar Logs do Render

No Render Dashboard:
1. Vá no serviço do backend
2. Clique em **Logs**
3. Procure por erros como:
   - `ModuleNotFoundError`
   - `ImportError`
   - `AttributeError`
   - `Failed to find attribute 'app'`

### 5. Verificar Configuração do Backend

No Render Dashboard, verifique:
- **Start Command**: Deve ser `gunicorn wsgi:app` ou usar o `Procfile`
- **Environment Variables**: 
  - `ENVIRONMENT=prd`
  - `DATABASE_URL` configurado
  - `SECRET_KEY` configurado

### 6. Verificar se o Deploy Foi Concluído

No Render Dashboard:
- Verifique se o último deploy foi bem-sucedido
- Se houver erro, faça um novo deploy manual

## 🔧 Soluções Comuns

### Solução 1: Backend está "Sleeping"

O Render coloca serviços gratuitos em "sleep" após inatividade.

**Solução:**
- A primeira requisição pode demorar ~30 segundos para "acordar" o serviço
- Aguarde alguns segundos e tente novamente

### Solução 2: Blueprint não está registrado

**Verificar:**
1. Acesse os logs do Render
2. Procure por: `Registering blueprint api`
3. Se não aparecer, há erro na importação

**Solução:**
- Verifique se `app/api/routes.py` existe
- Verifique se não há erros de sintaxe
- Faça um novo deploy

### Solução 3: URL Incorreta

**Verificar:**
- A URL do backend está correta?
- O serviço está em `voxen-pi4v.onrender.com` ou outro domínio?

**Solução:**
- Verifique a URL real no Render Dashboard
- Atualize a variável `VITE_API_BASE_URL` no frontend

### Solução 4: CORS Bloqueando

Se o erro for no navegador (não 404, mas CORS):

**Solução:**
- Verifique se o CORS está configurado no backend
- Verifique se a origem do frontend está permitida

## 📋 Checklist de Diagnóstico

- [ ] Backend está "Live" no Render (não "Sleeping")
- [ ] `/health` retorna `{"status": "ok"}`
- [ ] `/api/v1/test` retorna sucesso
- [ ] `/api/v1/` retorna informações da API
- [ ] Logs do Render não mostram erros
- [ ] Último deploy foi bem-sucedido
- [ ] Variáveis de ambiente estão configuradas
- [ ] URL do backend está correta

## 🆘 Se Nada Funcionar

1. **Faça um novo deploy manual:**
   - No Render Dashboard → Manual Deploy → Deploy latest commit

2. **Verifique os logs em tempo real:**
   - Acesse os logs enquanto faz uma requisição
   - Veja se há erros sendo gerados

3. **Teste localmente:**
   ```bash
   python wsgi.py
   # Em outro terminal:
   curl http://localhost:5000/api/v1/test
   ```

4. **Verifique se o código está atualizado:**
   ```bash
   git pull
   # Verifique se as alterações foram aplicadas
   ```

