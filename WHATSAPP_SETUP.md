# Guia de Configuração - WhatsApp Business API

## ⚠️ IMPORTANTE: Entendendo a API Oficial

**A API oficial do WhatsApp Business é da Meta/Facebook, MAS:**

- ❌ **NÃO é possível acessar diretamente** a API da Meta
- ✅ **É OBRIGATÓRIO usar um BSP** (Business Solution Provider) autorizado
- ✅ O BSP é o intermediário entre você e a API oficial da Meta


---

## 📋 Passos Antes de Implementar o Código

### 1. Escolher o BSP (Business Solution Provider) - OBRIGATÓRIO

**Mesmo usando a API oficial, você PRECISA de um BSP!**

Recomendação: **Twilio** (mais simples e econômico para começar)

**Opções de BSPs Autorizados:**
- **Twilio**: https://www.twilio.com (Recomendado - mais simples)
- **MessageBird**: https://www.messagebird.com
- **360dialog**: https://www.360dialog.com
- **Wati**: https://www.wati.io
- **Botmaker**: https://botmaker.com
- Outros BSPs autorizados pela Meta

**Todos usam a mesma API oficial da Meta, apenas facilitam o acesso.**

---

### 2. Criar Conta no BSP Escolhido (exemplo: Twilio)

#### 2.1. Criar Conta
1. Acesse: https://www.twilio.com/try-twilio
2. Crie uma conta gratuita
3. Verifique seu email e telefone

#### 2.2. Obter Credenciais
Após criar a conta, você precisará de:
- **Account SID**: Encontrado no Dashboard
- **Auth Token**: Encontrado no Dashboard
- **WhatsApp Sandbox Number**: Número de teste (inicialmente)

**Onde encontrar:**
- Dashboard → Account Info → Account SID e Auth Token
- Console → Messaging → Try it out → WhatsApp Sandbox

---

### 3. Criar Conta no Facebook Business Manager (OBRIGATÓRIO)

**IMPORTANTE:** Mesmo usando um BSP, você também precisa de:

1. Acesse: https://business.facebook.com
2. Crie uma conta no Facebook Business Manager
3. Verifique sua empresa/negócio
4. Este é necessário para aprovar seu número de WhatsApp Business

**Por quê?** A Meta exige que você tenha uma conta Business Manager para usar a API oficial.

---

### 4. Configurar WhatsApp Business API via BSP

#### 4.1. Aprovar Número de WhatsApp (Twilio - Sandbox para Testes)
1. No Twilio Console, vá em **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Siga as instruções para conectar seu número de WhatsApp
3. Você receberá um código para enviar via WhatsApp
4. Após aprovar, seu número estará conectado

**Sandbox:** Gratuito, apenas para testes, números limitados

#### 4.2. Obter Número WhatsApp Business (Produção)
Para produção, você precisará:
- Aprovar seu número de WhatsApp Business com a Meta (via BSP)
- Processo pode levar alguns dias
- Requer verificação de negócio no Facebook Business Manager
- O BSP (Twilio) faz a ponte entre você e a Meta

**Para testes iniciais:** Use o Sandbox do Twilio (gratuito)

---

### 5. Obter Credenciais Necessárias

Você precisará coletar as seguintes informações:

#### Para Twilio:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Número do Sandbox (teste)
```

#### Para outros BSPs:
- Consulte a documentação do BSP escolhido
- Geralmente precisará de: API Key, API Secret, Número de WhatsApp

---

### 6. Configurar Variáveis de Ambiente

#### 5.1. Local (Desenvolvimento)

Crie/edite o arquivo `.env` na raiz do projeto:

```bash
# WhatsApp - Twilio
TWILIO_ACCOUNT_SID=seu_account_sid_aqui
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Configurações de Notificação
WHATSAPP_ENABLED=true
WHATSAPP_NOTIFY_DAYS_BEFORE=3  # Notificar 3 dias antes do vencimento
WHATSAPP_NOTIFY_ON_DUE_DATE=true  # Notificar no dia do vencimento
WHATSAPP_NOTIFY_OVERDUE=true  # Notificar pagamentos em atraso
```

#### 5.2. Render (Produção)

No painel do Render, adicione as variáveis de ambiente:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `WHATSAPP_ENABLED=true`
- `WHATSAPP_NOTIFY_DAYS_BEFORE=3`
- `WHATSAPP_NOTIFY_ON_DUE_DATE=true`
- `WHATSAPP_NOTIFY_OVERDUE=true`

---

### 7. Testar Conexão (Opcional, mas Recomendado)

Antes de implementar, teste se consegue enviar uma mensagem:

```python
# test_whatsapp.py (criar este arquivo temporário)
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_WHATSAPP_FROM')

client = Client(account_sid, auth_token)

# Enviar mensagem de teste
message = client.messages.create(
    from_=from_number,
    body='Teste de mensagem WhatsApp',
    to='whatsapp:+5511999999999'  # Seu número de WhatsApp
)

print(f"Mensagem enviada! SID: {message.sid}")
```

**Execute:**
```bash
pip install twilio
python test_whatsapp.py
```

---

### 8. Decidir Configurações do Sistema

Antes de implementar, defina:

#### 7.1. Quando Enviar Notificações?
- [ ] X dias antes do vencimento (ex: 3 dias)
- [ ] No dia do vencimento
- [ ] Após vencimento (quantos dias de atraso?)

#### 7.2. Para Quem Enviar?
- [ ] Aluno (telefone do aluno)
- [ ] Responsável (telefone do responsável)
- [ ] Ambos

#### 7.3. Conteúdo da Mensagem
- Nome do aluno
- Data de vencimento
- Valor da mensalidade
- Modalidades
- Link para enviar comprovante (opcional)

#### 7.4. Frequência
- [ ] Uma vez por dia (verificar todos os vencimentos)
- [ ] Horário específico (ex: 9h da manhã)
- [ ] Apenas quando necessário

---

### 9. Checklist Final Antes de Implementar

- [ ] Conta criada no BSP (Twilio ou outro)
- [ ] Credenciais obtidas (Account SID, Auth Token)
- [ ] Número de WhatsApp configurado (Sandbox ou Produção)
- [ ] Teste de envio funcionando
- [ ] Variáveis de ambiente configuradas no `.env`
- [ ] Decisões sobre configurações do sistema tomadas
- [ ] Números de telefone dos alunos no formato correto (+55 11 987654321)

---

### 10. Formato de Telefone Necessário

Os telefones no banco devem estar no formato:
```
+55 11 987654321
```

**Verificar no banco:**
```sql
SELECT id, nome, telefone, telefone_responsavel 
FROM alunos 
WHERE telefone NOT LIKE '+%' OR telefone_responsavel NOT LIKE '+%';
```

Se houver telefones em formato incorreto, será necessário normalizá-los antes de enviar.

---

### 11. Próximos Passos (Após Configuração)

Após completar todos os passos acima, você estará pronto para:
1. ✅ Implementar o código de envio de mensagens
2. ✅ Criar o serviço de notificações
3. ✅ Configurar tarefas agendadas (cron jobs)
4. ✅ Criar interface administrativa

---

## 📞 Suporte

Se tiver dúvidas durante a configuração:
- **Twilio Docs**: https://www.twilio.com/docs/whatsapp
- **Twilio Support**: https://support.twilio.com

---

## ⚠️ Importante

### Resumo: O que é Obrigatório?

Para usar a **API oficial** do WhatsApp Business, você PRECISA de:

1. ✅ **Conta no Facebook Business Manager** (obrigatório)
2. ✅ **Conta em um BSP autorizado** (obrigatório - ex: Twilio)
3. ✅ **Número de WhatsApp Business aprovado** (obrigatório)

**Não é possível usar a API oficial sem esses 3 itens!**

### 1. Sandbox vs Produção
- **Sandbox**: Gratuito, apenas para testes, números limitados
- **Produção**: Requer aprovação da Meta, custa por conversa

### 2. Limites do Sandbox
- Apenas números pré-aprovados podem receber mensagens
- Ideal para desenvolvimento e testes
- Não é para uso em produção

### 3. Custos
- **Sandbox**: Gratuito
- **Produção**: ~R$ 0,038 por conversa (tarifa da Meta) + possíveis taxas do BSP

### 4. Por que usar BSP?
- A Meta não permite acesso direto à API
- BSPs facilitam integração, fornecem suporte e infraestrutura
- Todos os BSPs usam a mesma API oficial da Meta

### 5. Segurança
- Nunca commite credenciais no Git
- Use sempre variáveis de ambiente
- O arquivo `.env` já está no `.gitignore`

