# Migração: Criar Tabela horarios_professor

Este guia explica como criar a tabela `horarios_professor` e a coluna `modalidade` no banco de dados de produção.

## 📋 O que este script faz

1. **Cria a tabela `horarios_professor`** (se não existir)
   - Campos: `id`, `professor_id`, `dia_semana`, `horario_aula`, `modalidade`, `idade_minima`, `idade_maxima`
   - Foreign key para `professores.id`

2. **Adiciona a coluna `modalidade`** (se a tabela já existir mas a coluna não)
   - Tipo: `VARCHAR(50)`
   - Valor padrão: `'dublagem_presencial'`
   - NOT NULL

3. **Atualiza horários existentes** (se houver)
   - Tenta inferir a modalidade baseado nas modalidades do professor
   - Se não conseguir, usa `'dublagem_presencial'` como padrão

## 🚀 Como Executar

### Opção 1: Executar Localmente (Recomendado)

Se você tem acesso ao banco de produção via `DATABASE_URL`:

1. **Configure a variável de ambiente**:
   ```bash
   export DATABASE_URL="postgresql://usuario:senha@host:porta/database"
   ```
   
   Ou crie um arquivo `.env` na raiz do projeto:
   ```
   DATABASE_URL=postgresql://usuario:senha@host:porta/database
   ```

2. **Execute o script**:
   ```bash
   python criar_tabela_horarios_professor.py
   ```

3. **Verifique a saída**:
   - ✅ `✓ Tabela 'horarios_professor' criada com sucesso!`
   - ✅ `✓ Coluna 'modalidade' adicionada com sucesso!`

### Opção 2: Executar no Render (via Shell)

1. **Acesse o Shell do Render**:
   - No dashboard do Render, vá para seu **Web Service**
   - Clique em **"Shell"** (ou use o terminal SSH se disponível)

2. **Navegue até o diretório do projeto**:
   ```bash
   cd /opt/render/project/src
   ```

3. **Execute o script**:
   ```bash
   python criar_tabela_horarios_professor.py
   ```

### Opção 3: Executar via Python no Render

1. **Adicione uma rota temporária** no `app/routes.py`:
   ```python
   @bp.route('/migrar-horarios', methods=['GET'])
   @admin_required
   def migrar_horarios():
       from criar_tabela_horarios_professor import criar_tabela_horarios_professor
       try:
           criar_tabela_horarios_professor()
           flash('Migração executada com sucesso!', 'success')
       except Exception as e:
           flash(f'Erro na migração: {str(e)}', 'error')
       return redirect(url_for('main.listar_professores'))
   ```

2. **Acesse a rota** (apenas como admin):
   ```
   https://seu-app.onrender.com/migrar-horarios
   ```

3. **Remova a rota** após executar (por segurança)

## ✅ Verificação

Após executar o script, verifique:

1. **Acesse a rota de listar professores**:
   ```
   https://seu-app.onrender.com/professores
   ```

2. **Verifique se não há mais erro 500**

3. **Verifique se os horários aparecem** (se houver professores com horários cadastrados)

## 🔍 Troubleshooting

### Erro: "relation 'horarios_professor' does not exist"

**Causa**: A tabela não foi criada.

**Solução**: 
- Execute o script novamente
- Verifique os logs para ver o erro específico
- Verifique se a `DATABASE_URL` está correta

### Erro: "column 'modalidade' does not exist"

**Causa**: A coluna não foi adicionada.

**Solução**:
- Execute o script novamente
- O script detecta automaticamente se a coluna existe e só adiciona se necessário

### Erro: "could not connect to server"

**Causa**: Problema de conexão com o banco.

**Soluções**:
1. Verifique se a `DATABASE_URL` está correta
2. Verifique se o banco PostgreSQL está **Running** (não pausado)
3. Verifique se está usando `postgresql://` (não `postgres://`)

### Erro: "permission denied"

**Causa**: Usuário do banco não tem permissão para criar tabelas.

**Solução**:
- Verifique se o usuário do banco tem permissões de `CREATE TABLE`
- Se necessário, execute como superusuário do PostgreSQL

## 📝 Notas Importantes

- ⚠️ **Este script é idempotente**: Pode ser executado múltiplas vezes sem causar problemas
- ⚠️ **Backup recomendado**: Antes de executar em produção, faça backup do banco
- ⚠️ **Teste primeiro**: Se possível, teste em um banco de desenvolvimento antes

## 🎯 Próximos Passos

Após criar a tabela:

1. **Cadastre horários para os professores existentes** (se necessário)
2. **Verifique se a rota `/professores` está funcionando**
3. **Remova qualquer rota temporária de migração** que você tenha criado

