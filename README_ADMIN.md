# Como criar/atualizar o usuário administrador

## Problema
Após o deploy, o usuário admin padrão pode não estar funcionando porque o banco de dados de produção não foi inicializado com o usuário admin.

## Solução Segura

### ⚠️ IMPORTANTE: O script não contém senhas hardcoded por segurança!

### Opção 1: Fornecer username e senha como argumentos

```bash
python criar_admin.py admin minhasenha123
```

### Opção 2: Usar variáveis de ambiente (RECOMENDADO para produção)

```bash
ADMIN_USERNAME=admin ADMIN_PASSWORD=minhasenha123 python criar_admin.py
```

### Opção 3: Gerar senha aleatória automaticamente

Se você não fornecer uma senha, o script gerará uma senha aleatória segura:

```bash
python criar_admin.py admin
# ou apenas
python criar_admin.py
```

**⚠️ ATENÇÃO**: A senha será exibida apenas UMA VEZ. Anote imediatamente!

### Opção 4: Executar no ambiente de produção (Render)

Se você está usando Render:

1. **Via Shell do Render**:
   - Acesse o dashboard do Render
   - Vá em "Shell" do seu serviço
   - Execute com variáveis de ambiente:
     ```bash
     ADMIN_USERNAME=admin ADMIN_PASSWORD=suasenha123 python criar_admin.py
     ```

2. **Via variáveis de ambiente do Render**:
   - Configure as variáveis `ADMIN_USERNAME` e `ADMIN_PASSWORD` no dashboard do Render
   - Execute: `python criar_admin.py`

### Opção 5: Executar fix_database.py

O script `fix_database.py` também cria o usuário admin automaticamente se não existir (com senha padrão `admin123`):

```bash
python fix_database.py
```

**⚠️ NOTA**: O `fix_database.py` ainda usa a senha padrão `admin123` por compatibilidade, mas é recomendado alterá-la após a primeira execução usando `criar_admin.py`.

## Verificar usuários existentes

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

## Segurança

- ✅ O script `criar_admin.py` **NÃO** contém senhas hardcoded
- ✅ Senhas devem ser fornecidas via argumentos ou variáveis de ambiente
- ✅ Se nenhuma senha for fornecida, uma senha aleatória será gerada
- ✅ A senha é exibida apenas uma vez - anote imediatamente!
- ⚠️ Se o usuário admin já existir, a senha será **redefinida**
- ⚠️ Certifique-se de que o banco de dados de produção está configurado corretamente no `config.py`

