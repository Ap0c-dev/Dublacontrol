# Migração do Sandbox para Produção - WhatsApp Business

## ✅ Sim! Você Poderá Usar o Número da Sua Empresa

Quando começar a pagar e migrar para produção, você poderá configurar para usar o número de WhatsApp da sua empresa ao invés do número do Sandbox.

---

## 📋 Diferenças: Sandbox vs Produção

### Sandbox (Atual - Gratuito)
- ✅ Gratuito
- ❌ Número fixo: `+1 415 523 8886` (número do Twilio)
- ❌ Precisa aprovar cada número que vai receber
- ❌ Apenas para testes
- ❌ Limitações de uso

### Produção (Pago)
- ✅ Use seu próprio número de WhatsApp Business
- ✅ Não precisa aprovar números (clientes podem receber diretamente)
- ✅ Sem limitações de teste
- ✅ Custo: ~R$ 0,038 por conversa
- ⚠️ Requer aprovação do número Business com a Meta

---

## 🚀 Como Migrar para Produção

### Passo 1: Aprovar Número Business com a Meta

1. **Criar Conta no Facebook Business Manager**
   - Acesse: https://business.facebook.com
   - Crie uma conta Business Manager
   - Verifique sua empresa/negócio

2. **Conectar WhatsApp Business**
   - No Facebook Business Manager, vá em **WhatsApp**
   - Clique em **Adicionar número**
   - Siga o processo de verificação

3. **Aprovar Número com a Meta**
   - A Meta vai verificar seu negócio
   - Processo pode levar alguns dias
   - Você precisará fornecer documentos da empresa

### Passo 2: Conectar Número ao Twilio

1. **No Twilio Console**
   - Acesse: https://console.twilio.com
   - Vá em **Messaging** → **Settings** → **WhatsApp Senders**
   - Clique em **Add WhatsApp Sender**
   - Siga as instruções para conectar seu número Business

2. **Aguardar Aprovação**
   - O Twilio vai fazer a ponte entre você e a Meta
   - Processo pode levar alguns dias
   - Você receberá notificação quando estiver aprovado

### Passo 3: Atualizar Configuração no Sistema

Após aprovar, você precisará atualizar apenas **uma variável de ambiente**:

#### No arquivo `.env` (local):

```bash
# ANTES (Sandbox):
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# DEPOIS (Produção - seu número):
TWILIO_WHATSAPP_FROM=whatsapp:+5511999999999
# Substitua pelo número da sua empresa (formato: whatsapp:+5511999999999)
```

#### No Render (produção):

No painel do Render, atualize a variável:
- `TWILIO_WHATSAPP_FROM`: `whatsapp:+5511999999999` (seu número)

### Passo 4: Reiniciar Aplicação

Após atualizar, reinicie a aplicação:
```bash
# Local
python wsgi.py

# Render (deploy automático ao atualizar variáveis)
```

**Pronto!** Agora todas as mensagens serão enviadas do número da sua empresa.

---

## 💰 Custos

### Sandbox (Atual)
- **Gratuito**
- Sem custos

### Produção
- **Por conversa**: ~R$ 0,038 (tarifa da Meta)
- **Primeiras 1.000 conversas/mês**: Gratuitas
- **Exemplo**: 200 alunos notificados = ~R$ 7,60/mês

---

## ⚙️ Configuração Atual vs Produção

### Variáveis que NÃO mudam:
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_ENABLED=true
```

### Variável que MUDA:
```bash
# Sandbox:
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Produção (seu número):
TWILIO_WHATSAPP_FROM=whatsapp:+5511999999999
```

**Isso é tudo!** O código não precisa mudar, apenas a variável de ambiente.

---

## 📝 Checklist de Migração

- [ ] Criar conta no Facebook Business Manager
- [ ] Verificar empresa no Facebook Business Manager
- [ ] Adicionar número WhatsApp Business
- [ ] Aprovar número com a Meta (pode levar dias)
- [ ] Conectar número ao Twilio
- [ ] Aguardar aprovação do Twilio
- [ ] Atualizar `TWILIO_WHATSAPP_FROM` no `.env` e Render
- [ ] Reiniciar aplicação
- [ ] Testar envio de mensagem

---

## 🎯 Vantagens da Produção

1. **Número da Empresa**: Mensagens vêm do seu número, não do Twilio
2. **Sem Aprovação de Números**: Qualquer cliente pode receber
3. **Profissional**: Clientes veem seu número, não um número de teste
4. **Sem Limitações**: Pode enviar para qualquer número
5. **Escalável**: Suporta milhares de mensagens

---

## ⚠️ Importante

- **Sandbox**: Continue usando para testes até aprovar produção
- **Produção**: Use apenas após aprovação completa
- **Custos**: Produção tem custo por conversa (mas baixo)
- **Tempo**: Aprovação pode levar alguns dias/semanas

---

## 🔄 Migração Gradual

Você pode manter ambos configurados:

1. **Sandbox**: Para testes e desenvolvimento
2. **Produção**: Para clientes reais

Basta alternar a variável `TWILIO_WHATSAPP_FROM` conforme necessário.

---

## 📞 Suporte

Se precisar de ajuda na migração:
- **Twilio Support**: https://support.twilio.com
- **Meta Business Help**: https://www.facebook.com/business/help
- **Documentação Twilio**: https://www.twilio.com/docs/whatsapp

---

## ✅ Resumo

**SIM**, você poderá usar o número da sua empresa! Basta:
1. Aprovar número Business com a Meta
2. Conectar ao Twilio
3. Atualizar `TWILIO_WHATSAPP_FROM` no `.env`
4. Pronto! 🎉

O código já está preparado para isso - você só precisa mudar a variável de ambiente!



