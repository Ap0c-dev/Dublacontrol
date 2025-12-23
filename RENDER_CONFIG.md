# Configuração Rápida no Render

## ⚠️ Erro: "Failed to find attribute 'app' in 'app'"

Se você está vendo este erro, significa que o Render está tentando usar `gunicorn app:app` ao invés de `wsgi:app`.

## ✅ Solução

### Opção 1: Usar Procfile (Recomendado)

1. Certifique-se de que o `Procfile` está na raiz do projeto
2. No Render, **deixe o campo "Start Command" em branco**
3. O Render detectará automaticamente o `Procfile` e usará:
   ```
   gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
   ```

### Opção 2: Configurar Start Command Manualmente

No painel do Render, em **Settings** → **Build & Deploy**, configure:

**Start Command:**
```bash
gunicorn wsgi:app
```

**OU** (versão completa):
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
```

### Opção 3: Usar app.py (Alternativa)

Se as opções acima não funcionarem, você pode usar:
```bash
gunicorn app:app
```

O arquivo `app.py` foi criado na raiz e importa o app do `wsgi.py`.

## 📋 Checklist de Configuração no Render

- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: Deixar em branco (usa Procfile) OU `gunicorn wsgi:app`
- [ ] **Environment Variables** configuradas:
  - `ENVIRONMENT=prd`
  - `DATABASE_URL=<URL do PostgreSQL>`
  - `SECRET_KEY=<Chave secreta>`
  - `CLOUDINARY_*` (se usar upload de comprovantes)
  - `CORS_ORIGINS` (opcional, para restringir CORS)

## 🔍 Verificar se está funcionando

Após o deploy, acesse:
- `https://voxen.onrender.com/health` - Deve retornar `{"status": "ok"}`
- `https://voxen.onrender.com/api/v1/test` - Deve retornar `{"success": true, "message": "API está funcionando!"}`

