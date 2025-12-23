# Troubleshooting - Erro Internal Server Error

## Problema: Internal Server Error ao acessar `/notificacoes/testar`

### Soluções Possíveis:

### 1. Verificar se o Twilio está instalado

```bash
pip install twilio
```

Ou:

```bash
pip install -r requirements.txt
```

### 2. Verificar se o arquivo `.env` existe e está configurado

Certifique-se de que o arquivo `.env` na raiz do projeto contém:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_ENABLED=true
```

### 3. Reiniciar a aplicação Flask

Após adicionar/modificar o `.env`, **sempre reinicie a aplicação**:

```bash
# Parar a aplicação (Ctrl+C)
# Depois iniciar novamente:
python wsgi.py
```

### 4. Verificar logs do Flask

A aplicação deve mostrar no console:
- `✓ Arquivo .env carregado: /caminho/do/.env`
- Se houver erros de importação, eles aparecerão aqui

### 5. Verificar se o diretório `services` existe

Certifique-se de que existe:
- `app/services/__init__.py`
- `app/services/whatsapp_service.py`

### 6. Testar importação manual

No terminal Python:

```python
from app.services.whatsapp_service import WhatsAppService
```

Se der erro, verifique:
- Se o `twilio` está instalado: `pip list | grep twilio`
- Se há erros de sintaxe no arquivo

### 7. Verificar permissões

Certifique-se de que você está logado como **admin**:
- A rota requer `@admin_required`
- Se não for admin, será redirecionado

### 8. Verificar logs detalhados

Se ainda não funcionar, ative o modo debug do Flask:

```python
# Em wsgi.py ou onde inicia a app
app.run(debug=True)
```

Isso mostrará o traceback completo do erro.

---

## Erros Comuns e Soluções

### Erro: "ModuleNotFoundError: No module named 'twilio'"
**Solução:** `pip install twilio`

### Erro: "Cliente Twilio não inicializado"
**Solução:** Verifique se `TWILIO_ACCOUNT_SID` e `TWILIO_AUTH_TOKEN` estão no `.env`

### Erro: "Template not found: testar_notificacao.html"
**Solução:** Certifique-se de que o arquivo existe em `templates/testar_notificacao.html`

### Erro: "AttributeError: 'NoneType' object has no attribute 'config'"
**Solução:** Reinicie a aplicação Flask

---

## Teste Rápido

Execute este comando para verificar se tudo está OK:

```bash
python3 -c "
import os
os.chdir('/home/tiago/controle-dublagem')
from dotenv import load_dotenv
load_dotenv()
print('TWILIO_ACCOUNT_SID:', 'OK' if os.getenv('TWILIO_ACCOUNT_SID') else 'FALTANDO')
print('TWILIO_AUTH_TOKEN:', 'OK' if os.getenv('TWILIO_AUTH_TOKEN') else 'FALTANDO')
print('TWILIO_WHATSAPP_FROM:', os.getenv('TWILIO_WHATSAPP_FROM', 'FALTANDO'))
"
```

Se tudo estiver OK, você verá:
```
TWILIO_ACCOUNT_SID: OK
TWILIO_AUTH_TOKEN: OK
TWILIO_WHATSAPP_FROM: whatsapp:+14155238886
```

