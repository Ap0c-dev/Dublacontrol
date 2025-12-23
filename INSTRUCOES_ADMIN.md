# Como criar o usuário administrador no Render (sem Shell)

Como o Shell do Render é pago, você pode criar o usuário admin de duas formas:

## Opção 1: Via rota web (RECOMENDADO)

### Passo 1: Configurar variáveis de ambiente no Render

1. Acesse o dashboard do Render
2. Vá em seu serviço → "Environment"
3. Adicione as seguintes variáveis de ambiente:
   - `ENABLE_ADMIN_CREATION` = `true`
   - `ADMIN_CREATION_TOKEN` = `seu_token_secreto_aqui` (opcional, mas recomendado)

### Passo 2: Acessar a rota

1. Acesse a URL: `https://seu-app.onrender.com/criar-admin-inicial`
2. Preencha o formulário:
   - **Username**: admin (ou o que preferir)
   - **Senha**: escolha uma senha segura
   - **Token**: se você configurou `ADMIN_CREATION_TOKEN`, insira o token aqui
3. Clique em "Criar Usuário Administrador"

### Passo 3: Desativar a rota (IMPORTANTE!)

Após criar o admin, **IMEDIATAMENTE**:
1. Volte ao dashboard do Render
2. Remova ou defina `ENABLE_ADMIN_CREATION` como vazio/false
3. Isso desativa a rota por segurança

## Opção 2: Criação automática na inicialização

O sistema agora cria automaticamente um usuário admin padrão quando detecta que está em produção e não existe nenhum admin:

- **Username**: `admin`
- **Senha**: `[SENHA_GERADA_AUTOMATICAMENTE]`

⚠️ **IMPORTANTE**: 
- A senha padrão é gerada automaticamente
- Consulte os logs do servidor para obter a senha
- Altere a senha imediatamente após o primeiro login!

### Como verificar se foi criado:

1. Consulte os logs do servidor para obter a senha gerada
2. Tente fazer login com as credenciais obtidas dos logs

2. Se funcionar, altere a senha imediatamente através do sistema.

## Opção 3: Usar o script criar_admin.py localmente

Se você tem acesso ao banco de dados de produção de outra forma:

```bash
# Configurar variáveis de ambiente para apontar para o banco de produção
export DATABASE_URL="sua_url_do_banco"
python criar_admin.py admin minhasenha123
```

## Segurança

- ✅ A rota `/criar-admin-inicial` só funciona se `ENABLE_ADMIN_CREATION` estiver configurado
- ✅ Você pode adicionar um token adicional via `ADMIN_CREATION_TOKEN`
- ✅ **SEMPRE** desative `ENABLE_ADMIN_CREATION` após criar o admin
- ✅ Altere a senha padrão imediatamente após o primeiro login

