# Migração para Voxen - Gestão Escolar

Este documento explica como migrar do projeto antigo (dublacontrol.onrender.com) para a nova estrutura Voxen (voxen.onrender.com).

## 🎯 Objetivo

Migrar completamente para a nova estrutura moderna:
- ✅ Backend: API REST Flask (`/api/v1/*`)
- ✅ Frontend: React + TypeScript + Vite (moderno)
- ✅ Novo domínio: `voxen.onrender.com`

## 📋 Checklist de Migração

### 1. Preparação

- [ ] Fazer backup do banco de dados atual
- [ ] Exportar dados importantes (alunos, professores, pagamentos, notas)
- [ ] Documentar configurações atuais (Cloudinary, Twilio, etc.)

### 2. Deploy no Render

#### Backend (API Flask)

1. Criar novo Web Service no Render:
   - **Name**: `voxen` ou `voxen-api`
   - **Repository**: Seu repositório GitHub
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`

2. Configurar variáveis de ambiente:
   ```
   ENVIRONMENT=prd
   DATABASE_URL=<URL do PostgreSQL>
   SECRET_KEY=<Chave secreta aleatória>
   CLOUDINARY_CLOUD_NAME=<Seu Cloudinary>
   CLOUDINARY_API_KEY=<Sua API Key>
   CLOUDINARY_API_SECRET=<Seu API Secret>
   CORS_ORIGINS=https://voxen-frontend.onrender.com,https://voxen.onrender.com
   ```

3. Configurar domínio customizado:
   - Settings → Custom Domain → `voxen.onrender.com`

#### Frontend (React)

1. Criar novo Static Site no Render:
   - **Name**: `voxen-frontend`
   - **Root Directory**: `frontend_lovable/connect-dashboard-main`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

2. Configurar variável de ambiente:
   ```
   VITE_API_BASE_URL=https://voxen.onrender.com/api/v1
   ```

### 3. Migração de Dados

Se você tem dados no projeto antigo que precisa migrar:

1. **Exportar dados do banco antigo**:
   ```bash
   # Conectar ao banco antigo e exportar
   sqlite3 banco_antigo.db .dump > backup.sql
   ```

2. **Importar no novo banco PostgreSQL**:
   - Ajustar formato SQL se necessário
   - Importar via psql ou interface do Render

3. **Verificar integridade**:
   - Verificar relacionamentos (foreign keys)
   - Verificar dados de usuários
   - Testar login com usuários migrados

### 4. Configuração de CORS

O CORS já está configurado para aceitar variável de ambiente `CORS_ORIGINS`.

**No Render (Backend)**, adicione:
```
CORS_ORIGINS=https://voxen-frontend.onrender.com,https://voxen.onrender.com
```

### 5. Testes

Após o deploy, testar:

- [ ] Login funciona
- [ ] Dashboard carrega dados
- [ ] Listagem de alunos funciona
- [ ] Listagem de professores funciona
- [ ] Listagem de pagamentos funciona
- [ ] Criação de aluno funciona
- [ ] Criação de professor funciona
- [ ] Upload de comprovante funciona
- [ ] Filtros funcionam corretamente

### 6. Desativar Projeto Antigo

Após confirmar que tudo está funcionando:

- [ ] Desativar o serviço antigo no Render (ou manter como backup temporário)
- [ ] Atualizar documentação com novo domínio
- [ ] Notificar usuários sobre a mudança

## 🔧 Configurações Importantes

### Variáveis de Ambiente do Backend

```env
ENVIRONMENT=prd
DATABASE_URL=postgresql://...
SECRET_KEY=<gerar chave aleatória>
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
CORS_ORIGINS=https://voxen-frontend.onrender.com,https://voxen.onrender.com
```

### Variáveis de Ambiente do Frontend

```env
VITE_API_BASE_URL=https://voxen.onrender.com/api/v1
```

## 📝 Notas

1. **Domínio**: O Render permite configurar domínios customizados. Para usar `voxen.onrender.com`, configure no painel do Render.

2. **SSL**: O Render fornece SSL automático.

3. **Banco de Dados**: Use PostgreSQL em produção. SQLite não é recomendado.

4. **Projeto Antigo**: Você pode manter o projeto antigo como backup temporário, mas recomenda-se usar apenas a nova estrutura.

## 🐛 Troubleshooting

### Erro de Login

Se encontrar erro "cannot access local variable 'username'", isso foi corrigido no código. Certifique-se de usar a versão mais recente.

### CORS Error

Verifique se `CORS_ORIGINS` está configurado corretamente no backend e se a URL do frontend está incluída.

### Database Connection

Verifique se `DATABASE_URL` está correta e se o banco PostgreSQL está acessível.

## ✅ Após Migração

- [ ] Todos os testes passando
- [ ] Usuários conseguem fazer login
- [ ] Dados migrados corretamente
- [ ] Frontend conectado ao backend
- [ ] Domínio customizado funcionando
- [ ] SSL funcionando
- [ ] Projeto antigo desativado (ou mantido como backup)

