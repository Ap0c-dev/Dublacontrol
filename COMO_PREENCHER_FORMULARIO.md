# Como Preencher o Formulário de Criação de Admin

## 📋 Campos do Formulário

Quando você acessar `https://seu-app.onrender.com/criar-admin-inicial`, verá 3 campos:

### 1️⃣ **Username do Administrador**
- **O que é**: O nome de usuário que você usará para fazer LOGIN no sistema
- **Exemplo**: `admin`
- **Dica**: Pode ser qualquer nome, mas "admin" é o padrão

### 2️⃣ **Senha do Administrador**
- **O que é**: A senha que você usará para fazer LOGIN no sistema
- **Exemplo**: `minhasenha123`
- **Requisito**: Mínimo 6 caracteres
- **Dica**: Escolha uma senha segura e anote em local seguro

### 3️⃣ **Token de Segurança** (só aparece se você configurou ADMIN_CREATION_TOKEN)
- **O que é**: Um código de segurança que você configurou no Render
- **Valor**: `o2T0av5pTA4XZvUPMP4-Sfri-9LO__Z4u5wotsm3QTk`
- **Onde pegar**: Você configurou este valor na variável `ADMIN_CREATION_TOKEN` no Render
- **Importante**: Este NÃO é a senha do admin, é apenas um código de segurança

## 📝 Exemplo de Preenchimento

```
Username do Administrador: admin
Senha do Administrador: MinhaSenhaSegura123!
Token de Segurança: o2T0av5pTA4XZvUPMP4-Sfri-9LO__Z4u5wotsm3QTk
```

## 🔐 Após Criar o Admin

Você poderá fazer login com:
- **Username**: `admin` (ou o que você digitou no campo 1)
- **Senha**: `MinhaSenhaSegura123!` (ou a que você digitou no campo 2)

**O token NÃO é usado para login**, apenas para validar que você tem permissão para criar o admin.

## ⚠️ Importante

Após criar o admin com sucesso:
1. Faça login no sistema
2. Volte ao Render e **REMOVA** a variável `ENABLE_ADMIN_CREATION` por segurança

