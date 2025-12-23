# 🔍 Verificar Usuário para Login

## Problema: "Credenciais inválidas"

Se você está recebendo erro de "Credenciais inválidas", pode ser por:

1. **Usuário não existe no banco de dados**
2. **Senha incorreta**
3. **Usuário está inativo**
4. **Senha foi criada incorretamente**

## ✅ Solução: Criar/Verificar Usuário

### Opção 1: Usar Script Python (Recomendado)

```bash
# Criar usuário admin
python criar_usuario.py admin admin SUA_SENHA_AQUI

# Criar usuário gerente
python criar_usuario.py gerente gerente SUA_SENHA_AQUI
```

### Opção 2: Via Interface Web (Render)

1. Configure no Render:
   - `ENABLE_ADMIN_CREATION=true`
   - `ADMIN_CREATION_TOKEN=seu_token_secreto`

2. Acesse:
   ```
   https://SEU_BACKEND.onrender.com/criar-admin-inicial
   ```

3. Crie o usuário e depois desative `ENABLE_ADMIN_CREATION`

### Opção 3: Verificar Usuários Existentes

Para verificar quais usuários existem:

```python
from app import create_app
from app.models.usuario import Usuario

app = create_app()
with app.app_context():
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"Username: {u.username}, Role: {u.role}, Ativo: {u.ativo}")
```

### Opção 4: Redefinir Senha de Usuário Existente

Se o usuário existe mas você esqueceu a senha:

```bash
# Redefinir senha do admin
python criar_usuario.py admin admin NOVA_SENHA_AQUI
```

## 🔍 Verificar no Console do Navegador

Abra o console (F12) e verifique:
- Se aparecer `❌ Tentativa de login com usuário inexistente`, o usuário não existe
- Se aparecer `❌ Tentativa de login com senha incorreta`, a senha está errada
- Se aparecer `❌ Tentativa de login com usuário inativo`, o usuário está desativado

## 📝 Notas

- O sistema agora fornece mensagens mais específicas nos logs do servidor
- Verifique os logs do Render para ver qual é o problema específico
- Use o script `criar_usuario.py` para criar ou atualizar usuários

