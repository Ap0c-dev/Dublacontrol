# Deploy Voxen - Gestão Escolar

Este documento explica como fazer o deploy da aplicação Voxen no Render com o novo domínio.

## 📋 Pré-requisitos

1. Conta no Render (https://render.com)
2. Repositório GitHub com o código
3. Banco de dados PostgreSQL (pode ser criado no Render)

## 🚀 Passo a Passo

### 1. Criar Banco de Dados PostgreSQL no Render

1. Acesse o dashboard do Render
2. Clique em **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `voxen-db` (ou o nome que preferir)
   - **Database**: `voxen` (ou o nome que preferir)
   - **User**: Deixe o padrão ou escolha um nome
   - **Region**: Escolha a região mais próxima
4. Clique em **Create Database**
5. **IMPORTANTE**: Copie a **Internal Database URL** (será usada depois)

### 2. Criar Web Service (Backend Flask)

1. No dashboard do Render, clique em **New +** → **Web Service**
2. Conecte seu repositório GitHub
3. Configure:
   - **Name**: `voxen` (ou `voxen-api`)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     gunicorn wsgi:app
     ```
     - **OU** deixe em branco para usar o `Procfile` automaticamente
     - **OU** use: `gunicorn app:app` (se criou o arquivo `app.py` na raiz)
   - **Plan**: Escolha o plano (Free tier disponível)

4. **Environment Variables** (adicionar):
   ```
   ENVIRONMENT=prd
   DATABASE_URL=<Internal Database URL do PostgreSQL>
   SECRET_KEY=<Gere uma chave secreta aleatória>
   CLOUDINARY_CLOUD_NAME=<Seu Cloudinary Cloud Name>
   CLOUDINARY_API_KEY=<Sua API Key do Cloudinary>
   CLOUDINARY_API_SECRET=<Seu API Secret do Cloudinary>
   ```

5. Clique em **Create Web Service**

6. **IMPORTANTE**: Após criar, vá em **Settings** → **Custom Domain** e configure:
   - **Custom Domain**: `voxen.onrender.com` (ou o domínio que preferir)
   - Render irá gerar automaticamente o certificado SSL

### 3. Criar Static Site (Frontend React)

⚠️ **IMPORTANTE**: O frontend React precisa ser configurado como um **Static Site separado**. Se você acessar o backend diretamente (`voxen.onrender.com`), verá a interface antiga (templates HTML do Flask).

1. No dashboard do Render, clique em **New +** → **Static Site**
2. Conecte seu repositório GitHub (o mesmo do backend)
3. Configure:
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

5. Clique em **Create Static Site**

6. Após o deploy, o frontend estará disponível em uma URL do Render (ex: `voxen-frontend.onrender.com`)

7. **Acesse o frontend pela URL do Static Site**, não pela URL do backend!
   - ✅ **Correto**: `https://voxen-frontend.onrender.com` (frontend React)
   - ❌ **Errado**: `https://SEU_BACKEND.onrender.com` (backend Flask com templates antigos)

### 4. Configurar CORS no Backend

O CORS já está configurado para permitir todas as origens (`*`). Se quiser restringir apenas ao seu frontend:

**No arquivo `app/__init__.py`**, linha 65, altere:

```python
"origins": ["https://voxen-frontend.onrender.com", "https://voxen.onrender.com"]
```

### 5. Primeiro Acesso

1. Acesse o backend: `https://voxen.onrender.com`
2. Acesse o frontend: `https://voxen-frontend.onrender.com` (ou o domínio configurado)
3. Faça login com suas credenciais

### 6. Criar Usuário Admin Inicial

Se precisar criar um usuário admin inicial, você pode:

1. Acessar via SSH no Render (se disponível)
2. Ou criar um script Python temporário para criar o admin

**Script para criar admin** (`criar_admin_voxen.py`):

```python
from app import create_app
from app.models.usuario import Usuario
from app.models.professor import db

app = create_app()

with app.app_context():
    # Verificar se já existe admin
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@voxen.com',
            role='admin',
            ativo=True
        )
        admin.set_password('[SENHA_TEMPORARIA]')  # ALTERE ESTA SENHA!
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin criado: username=admin, password=[CONSULTE_OS_LOGS]")
    else:
        print("⚠️ Admin já existe")
```

Execute no Render via SSH ou adicione como comando de build temporário.

## 🔧 Configurações Importantes

### Variáveis de Ambiente do Backend

- `ENVIRONMENT=prd` - Define ambiente de produção
- `DATABASE_URL` - URL do PostgreSQL (Render fornece automaticamente)
- `SECRET_KEY` - Chave secreta para sessões (gere uma aleatória)
- `CLOUDINARY_*` - Credenciais do Cloudinary para upload de comprovantes

### Variáveis de Ambiente do Frontend

- `VITE_API_BASE_URL` - URL completa da API backend

## 📝 Notas

1. **Domínio Customizado**: O Render permite configurar domínios customizados. Para usar `voxen.onrender.com`, configure no painel do Render.

2. **SSL**: O Render fornece SSL automático para todos os serviços.

3. **Banco de Dados**: Use PostgreSQL em produção. O SQLite não é recomendado para produção no Render.

4. **Migração de Dados**: Se você tem dados no projeto antigo, precisará migrar:
   - Exportar dados do banco antigo
   - Importar no novo banco PostgreSQL
   - Verificar relacionamentos e foreign keys

## 🐛 Troubleshooting

### Erro: "cannot access local variable 'username'"

Este erro geralmente vem do projeto antigo. Certifique-se de estar usando apenas a nova API (`/api/v1/auth/login`).

### CORS Error

Verifique se o CORS está configurado corretamente no `app/__init__.py` e se a URL do frontend está permitida.

### Database Connection Error

Verifique se a `DATABASE_URL` está correta e se o banco PostgreSQL está acessível.

## ✅ Checklist de Deploy

- [ ] Banco PostgreSQL criado no Render
- [ ] Web Service (Backend) criado e configurado
- [ ] Static Site (Frontend) criado e configurado
- [ ] Variáveis de ambiente configuradas
- [ ] Domínio customizado configurado
- [ ] CORS configurado corretamente
- [ ] Usuário admin criado
- [ ] Teste de login funcionando
- [ ] Teste de criação de aluno/professor funcionando

