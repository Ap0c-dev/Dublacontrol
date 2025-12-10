# Guia de Deploy no Render

## Pré-requisitos

1. Conta no Render (https://render.com)
2. Repositório GitHub conectado

## Passo a Passo

### 1. Criar Novo Web Service no Render

1. Acesse o dashboard do Render
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub: `Ap0c-dev/Dublacontrol`
4. Configure:
   - **Name**: `dublacontrol` (ou o nome que preferir)
   - **Region**: Escolha a região mais próxima
   - **Branch**: `main`
   - **Root Directory**: (deixe vazio)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 2. Configurar Variáveis de Ambiente

No painel do Render, vá em "Environment" e adicione:

- **SECRET_KEY**: Gere uma chave aleatória (ex: `python -c "import secrets; print(secrets.token_hex(32))"`)
- **DATABASE_URL**: (Opcional) Se criar um banco PostgreSQL no Render, será fornecido automaticamente

### 3. Banco de Dados (Recomendado)

**Opção 1: PostgreSQL no Render (Recomendado para produção)**
1. No Render, crie um "PostgreSQL" database
2. O Render fornecerá automaticamente a variável `DATABASE_URL`
3. A aplicação detectará e usará automaticamente

**Opção 2: SQLite (Apenas para testes)**
- Se não configurar `DATABASE_URL`, usará SQLite
- ⚠️ **Atenção**: No Render, o sistema de arquivos é efêmero
- Os dados serão perdidos quando o serviço reiniciar
- Use apenas para testes!

### 4. Deploy

1. Clique em "Create Web Service"
2. O Render iniciará o build automaticamente
3. Aguarde o deploy completar
4. Sua aplicação estará disponível em: `https://seu-app.onrender.com`

## Arquivos Importantes

- **Procfile**: Define como iniciar a aplicação (`web: gunicorn app:app`)
- **requirements.txt**: Lista todas as dependências
- **config.py**: Configurações que detectam automaticamente o ambiente Render

## Troubleshooting

### Tela "WELCOME TO RENDER" ou aplicação não carrega

**Possíveis causas e soluções:**

1. **Serviço em modo sleep (plano gratuito)**
   - O Render coloca serviços gratuitos em sleep após 15 minutos de inatividade
   - A primeira requisição pode demorar até 1 minuto para "acordar" o serviço
   - Aguarde alguns segundos e recarregue a página

2. **Erro na inicialização**
   - Verifique os logs no painel do Render (aba "Logs")
   - Procure por erros de importação ou banco de dados
   - Verifique se todas as dependências estão no `requirements.txt`

3. **Banco de dados não configurado**
   - Se usar PostgreSQL, certifique-se de que o banco está criado e ativo
   - Verifique se a variável `DATABASE_URL` está configurada
   - Para SQLite, os dados serão perdidos ao reiniciar (não recomendado para produção)

4. **Problemas com caminhos**
   - A aplicação detecta automaticamente os caminhos dos templates
   - Se houver erro, verifique os logs

### Erro: "No module named 'gunicorn'"
- Verifique se o `requirements.txt` contém `gunicorn==21.2.0`

### Erro: "Database connection failed"
- Verifique se a variável `DATABASE_URL` está configurada corretamente
- Se usar PostgreSQL, certifique-se de que o banco está ativo
- Verifique se o formato da URL está correto (postgresql:// não postgres://)

### Erro: "Application failed to respond"
- Verifique os logs no Render
- Certifique-se de que o `Procfile` está correto
- Verifique se a porta está sendo lida da variável `PORT` (Render define automaticamente)
- Teste a rota `/health` para verificar se a aplicação está respondendo

## Notas Importantes

1. **Primeira execução**: As tabelas serão criadas automaticamente na primeira requisição
2. **Migrações**: Se precisar migrar dados, execute o script `fix_database.py` localmente antes do deploy
3. **Logs**: Acesse os logs em tempo real no painel do Render
4. **SSL**: O Render fornece HTTPS automaticamente

