# Implementação de Notificações WhatsApp - Guia Completo

## ✅ O que foi implementado

1. **Serviço WhatsApp** (`app/services/whatsapp_service.py`)
   - Envio de mensagens via Twilio
   - Formatação automática de telefones
   - Criação de mensagens de vencimento personalizadas
   - Notificação automática de alunos com vencimento hoje

2. **Rotas de Notificação** (`app/routes.py`)
   - `/notificacoes/enviar-vencimentos` - Envia notificações (admin)
   - `/notificacoes/testar` - Página para testar envio manual

3. **Script para Cron Job** (`enviar_notificacoes.py`)
   - Executa automaticamente todos os dias
   - Envia notificações para alunos com vencimento hoje

4. **Configurações** (`config.py`)
   - Variáveis de ambiente para WhatsApp/Twilio

---

## 🔧 Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Isso instalará o `twilio` automaticamente.

### 2. Configurar Variáveis de Ambiente

#### Local (Desenvolvimento)

Edite o arquivo `.env` na raiz do projeto:

```bash
# WhatsApp - Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_ENABLED=true
```

#### Render (Produção)

No painel do Render, adicione as variáveis de ambiente:
- `TWILIO_ACCOUNT_SID`: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- `TWILIO_AUTH_TOKEN`: `6ae18b228e7cf6cc36271f45f80df07d`
- `TWILIO_WHATSAPP_FROM`: `whatsapp:+14155238886`
- `WHATSAPP_ENABLED`: `true`

---

## 📱 Como Usar

### 1. Testar Envio Manual

1. Acesse: `http://localhost:5000/notificacoes/testar` (ou sua URL)
2. Preencha:
   - **Telefone**: Seu número (formato: `+55 11 987654321`)
   - **Mensagem**: Mensagem de teste
3. Clique em "Enviar Mensagem de Teste"
4. Verifique se recebeu no WhatsApp

### 2. Enviar Notificações de Vencimento (Manual)

**Opção A: Via Interface Web (em desenvolvimento)**
- Adicionar botão na página de listar alunos
- Botão "Enviar Notificações de Vencimento"

**Opção B: Via Rota Direta**
- Acesse: `http://localhost:5000/notificacoes/enviar-vencimentos` (POST)
- Ou use curl:
```bash
curl -X POST http://localhost:5000/notificacoes/enviar-vencimentos \
  -H "Cookie: session=seu_session_cookie"
```

### 3. Configurar Execução Automática (Cron Job)

#### Local (Linux/Mac)

1. Edite o crontab:
```bash
crontab -e
```

2. Adicione a linha (executa todo dia às 9h):
```bash
0 9 * * * cd /home/tiago/controle-dublagem && /usr/bin/python3 enviar_notificacoes.py >> notificacoes_cron.log 2>&1
```

**Ajuste o caminho** conforme necessário:
- `/home/tiago/controle-dublagem` - caminho do projeto
- `/usr/bin/python3` - caminho do Python 3

#### Render (Produção)

No Render, você pode usar um **Cron Job**:

1. No dashboard do Render, vá em **Cron Jobs**
2. Clique em "New Cron Job"
3. Configure:
   - **Name**: `Enviar Notificações WhatsApp`
   - **Schedule**: `0 9 * * *` (todo dia às 9h)
   - **Command**: `cd /opt/render/project/src && python3 enviar_notificacoes.py`
   - **Service**: Selecione seu web service

**Ou** use um serviço externo como:
- **Cronitor**: https://cronitor.io
- **EasyCron**: https://www.easycron.com
- **UptimeRobot**: https://uptimerobot.com (com webhook)

---

## 📋 Formato de Mensagem

A mensagem enviada será:

```
Olá, [Nome do Aluno]!

📅 Lembrete: Sua mensalidade vence hoje ([DD/MM/YYYY]).

💰 Valor: R$ [valor]
📚 Modalidades: [lista de modalidades]

Para enviar o comprovante de pagamento, acesse o sistema.

Atenciosamente,
Equipe de Dublagem
```

---

## 🔍 Verificação

### Verificar se está funcionando:

1. **Teste manual**: Use a página `/notificacoes/testar`
2. **Verificar logs**: 
   - Local: `notificacoes.log`
   - Render: Logs do serviço
3. **Verificar alunos**: Certifique-se de que há alunos com `data_vencimento = hoje` e `ativo = True`

### Troubleshooting

#### Erro: "Cliente Twilio não inicializado"
- Verifique se as credenciais estão no `.env`
- Reinicie a aplicação após adicionar variáveis

#### Erro: "Telefone inválido"
- Verifique o formato do telefone no banco
- Deve estar no formato: `+55 11 987654321`

#### Erro: "WhatsApp não está habilitado"
- Verifique se `WHATSAPP_ENABLED=true` no `.env`

#### Mensagens não chegam
- Verifique se o número está aprovado no Sandbox do Twilio
- Verifique os logs do Twilio no dashboard
- Verifique se há créditos na conta Twilio

---

## 📊 Próximas Melhorias (Opcional)

1. **Histórico de Notificações**
   - Criar tabela para armazenar notificações enviadas
   - Exibir histórico na interface

2. **Configurações Avançadas**
   - Permitir configurar quantos dias antes notificar
   - Personalizar mensagem por aluno

3. **Notificações Múltiplas**
   - Notificar X dias antes
   - Notificar no dia
   - Notificar após vencimento

4. **Interface Administrativa**
   - Botão na página de alunos
   - Dashboard de notificações
   - Relatórios de envio

---

## ✅ Checklist de Implementação

- [x] Serviço WhatsApp criado
- [x] Rotas de notificação implementadas
- [x] Script para cron job criado
- [x] Configurações adicionadas ao config.py
- [x] Template de teste criado
- [ ] Botão na interface de alunos (opcional)
- [ ] Configurar cron job (você precisa fazer)
- [ ] Testar envio de mensagens
- [ ] Verificar formato dos telefones no banco

---

## 🚀 Próximos Passos

1. **Agora**: Configure as variáveis de ambiente no `.env`
2. **Teste**: Use `/notificacoes/testar` para testar
3. **Configure**: Adicione o cron job para execução automática
4. **Monitore**: Verifique os logs regularmente

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs (`notificacoes.log`)
2. Verifique o dashboard do Twilio
3. Verifique se as variáveis de ambiente estão corretas

