# 👥 Como Criar Usuários Admin e Gerente

Este guia explica como criar usuários com diferentes roles (admin, gerente, professor, aluno) no sistema Voxen.

## 📋 Roles Disponíveis

- **admin**: Acesso total ao sistema, pode criar, editar e excluir tudo
- **gerente**: Pode visualizar tudo, mas não pode editar (somente leitura)
- **professor**: Acesso apenas às abas Alunos e Notas, vê somente seus próprios alunos
- **aluno**: Acesso apenas aos seus próprios dados e notas

## 🚀 Métodos para Criar Usuários

### Método 1: Script Python (Recomendado)

#### Criar Usuário Admin

```bash
# Opção 1: Com username e senha
python criar_usuario.py admin admin SUA_SENHA_SEGURA_AQUI

# Opção 2: Com variáveis de ambiente
ROLE=admin USERNAME=admin PASSWORD=SUA_SENHA_SEGURA_AQUI python criar_usuario.py

# Opção 3: Gerar senha aleatória automaticamente
python criar_usuario.py admin admin
```

#### Criar Usuário Gerente

```bash
# Opção 1: Com username e senha
python criar_usuario.py gerente gerente SUA_SENHA_SEGURA_AQUI

# Opção 2: Com variáveis de ambiente
ROLE=gerente USERNAME=gerente PASSWORD=SUA_SENHA_SEGURA_AQUI python criar_usuario.py

# Opção 3: Gerar senha aleatória automaticamente
python criar_usuario.py gerente gerente
```

#### Criar Usuário Professor

```bash
python criar_usuario.py professor professor1 SUA_SENHA_SEGURA_AQUI
```

#### Criar Usuário Aluno

```bash
python criar_usuario.py aluno aluno1 SUA_SENHA_SEGURA_AQUI
```

### Método 2: Via Interface Web (Render)

Se você está usando Render e não tem acesso ao shell:

1. **Configure variáveis de ambiente no Render:**
   - `ENABLE_ADMIN_CREATION=true`
   - `ADMIN_CREATION_TOKEN=seu_token_secreto` (opcional, mas recomendado)

2. **Acesse a URL:**
   ```
   https://SEU_BACKEND.onrender.com/criar-admin-inicial
   ```
   (Substitua `SEU_BACKEND` pela URL real do seu backend)

3. **Preencha o formulário:**
   - Username: `admin` (ou o que preferir)
   - Senha: escolha uma senha segura
   - Token: se configurou `ADMIN_CREATION_TOKEN`, insira aqui

4. **⚠️ IMPORTANTE**: Após criar, desative `ENABLE_ADMIN_CREATION` por segurança!

### Método 3: Via Shell do Render (se disponível)

Se você tem acesso ao Shell do Render:

```bash
# Criar admin
ROLE=admin USERNAME=admin PASSWORD=SUA_SENHA_SEGURA_AQUI python criar_usuario.py

# Criar gerente
ROLE=gerente USERNAME=gerente PASSWORD=SUA_SENHA_SEGURA_AQUI python criar_usuario.py
```

### Método 4: Criação Automática na Inicialização

O sistema cria automaticamente um usuário admin padrão quando:
- Está em produção (`ENVIRONMENT=prd`)
- Não existe nenhum usuário com role `admin`

**Credenciais padrão:**
- Username: `admin`
- Senha: `[SENHA_PADRAO_TEMPORARIA]`

⚠️ **IMPORTANTE**: 
- A senha padrão é gerada automaticamente e deve ser alterada imediatamente após o primeiro login
- Consulte os logs do servidor para obter a senha padrão gerada

## 🔐 Exemplos Práticos

### Criar múltiplos usuários

```bash
# Admin principal
python criar_usuario.py admin admin SUA_SENHA_ADMIN_SEGURA

# Gerente
python criar_usuario.py gerente gerente SUA_SENHA_GERENTE_SEGURA

# Segundo admin (backup)
python criar_usuario.py admin admin2 SUA_SENHA_ADMIN2_SEGURA
```

### Criar com senha aleatória

```bash
# O script gerará uma senha aleatória e exibirá na tela
python criar_usuario.py admin admin
# Anote a senha exibida!
```

## 🔍 Verificar Usuários Existentes

Para verificar quais usuários existem no banco:

```python
from app import create_app
from app.models.usuario import Usuario

app = create_app()
with app.app_context():
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"Username: {u.username}, Role: {u.role}, Ativo: {u.ativo}")
```

## ⚠️ Segurança

1. **Sempre use senhas fortes** (mínimo 8 caracteres, com letras, números e símbolos)
2. **Não compartilhe credenciais** por email ou mensagens não criptografadas
3. **Altere senhas padrão** imediatamente após o primeiro login
4. **Desative rotas de criação** após criar os usuários iniciais
5. **Use tokens** para criação via web quando possível

## 🐛 Troubleshooting

### Erro: "Role inválido"
- Verifique se o role está correto: `admin`, `gerente`, `professor`, ou `aluno`
- O role é case-insensitive (pode ser maiúscula ou minúscula)

### Erro: "Username já existe"
- O script atualizará a senha e role do usuário existente
- Se quiser criar um usuário diferente, use outro username

### Erro: "Database connection failed"
- Verifique se o banco de dados está acessível
- Verifique se as variáveis de ambiente estão configuradas corretamente

## 📝 Notas

- O script `criar_usuario.py` substitui o antigo `criar_admin.py` com mais funcionalidades
- Você pode usar `criar_admin.py` ainda, mas ele só cria usuários admin
- Usuários criados via script são automaticamente ativados (`ativo=True`)

