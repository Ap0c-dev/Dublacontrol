# Como Usar ngrok para Expor Flask Localmente

## O que é ngrok?

O ngrok cria um túnel seguro que expõe seu servidor local (localhost:5000) para a internet, permitindo que o Lovable acesse sua API mesmo estando em um servidor remoto.

---

## 📥 Instalação

### Linux (Ubuntu/Debian)

```bash
# Baixar ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extrair
tar -xzf ngrok-v3-stable-linux-amd64.tgz

# Mover para /usr/local/bin (opcional, para usar de qualquer lugar)
sudo mv ngrok /usr/local/bin/

# Ou deixar na pasta do projeto
```

### Verificar Instalação

```bash
ngrok version
```

---

## 🔐 Configuração Inicial (OBRIGATÓRIO)

O ngrok agora **requer uma conta gratuita** e authtoken.

### Passo 1: Criar Conta no ngrok

1. Acesse: https://dashboard.ngrok.com/signup
2. Crie uma conta gratuita (é grátis!)
3. Faça login

### Passo 2: Obter Authtoken

1. Após fazer login, acesse: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copie o authtoken que aparece (algo como: `2abc123def456ghi789jkl012mno345pq_6r7s8t9u0v1w2x3y4z5`)

### Passo 3: Configurar Authtoken

No terminal, execute:

```bash
ngrok config add-authtoken SEU_AUTHTOKEN_AQUI
```

Substitua `SEU_AUTHTOKEN_AQUI` pelo token que você copiou.

**Exemplo:**
```bash
ngrok config add-authtoken 2abc123def456ghi789jkl012mno345pq_6r7s8t9u0v1w2x3y4z5
```

Você verá: `Authtoken saved to configuration file: /home/tiago/.ngrok2/ngrok.yml`

---

## 🚀 Como Usar

### Passo 1: Iniciar Flask

Em um terminal, inicie o Flask:

```bash
cd /home/tiago/controle-dublagem
python wsgi.py
```

Deixe rodando.

### Passo 2: Iniciar ngrok

Em outro terminal, execute:

```bash
ngrok http 5000
```

Agora deve funcionar!

Você verá algo como:

```
ngrok                                                                              
                                                                                   
Session Status                online                                               
Account                       seu-email@exemplo.com (Plan: Free)                   
Version                       3.x.x                                                 
Region                        United States (us)                                    
Latency                      45ms                                                  
Web Interface                 http://127.0.0.1:4040                                
Forwarding                    https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:5000
                                                                                   
Connections                   ttl     opn     rt1     rt5     p50     p90          
                              0       0       0.00    0.00    0.00    0.00         
```

### Passo 3: Copiar URL do ngrok

Copie a URL que aparece em "Forwarding":
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

### Passo 4: Usar no Lovable

No Lovable, configure a URL base da API como:
```
https://xxxx-xx-xx-xx-xx.ngrok-free.app/api/v1
```

**Substitua** `xxxx-xx-xx-xx-xx.ngrok-free.app` pela URL que o ngrok gerou.

---

## 🔧 Configuração Avançada (Opcional)

### Criar Conta Gratuita (Recomendado)

1. Acesse: https://dashboard.ngrok.com/signup
2. Crie uma conta gratuita
3. Obtenha seu authtoken
4. Configure:

```bash
ngrok config add-authtoken SEU_TOKEN_AQUI
```

**Vantagens:**
- URLs fixas (não mudam a cada reinício)
- Sem limite de tempo
- Mais estável

### Usar URL Fixa (Com Conta)

```bash
ngrok http 5000 --domain=seu-dominio.ngrok-free.app
```

---

## ⚠️ Importante

### 1. URL Muda a Cada Reinício (Sem Conta)

Se você não tiver conta no ngrok, a URL muda toda vez que reiniciar. Para evitar isso:
- Crie conta gratuita no ngrok
- Use `--domain` para URL fixa

### 2. Aviso do ngrok (Plano Gratuito)

O plano gratuito mostra uma página de aviso na primeira vez. Isso é normal. Você pode:
- Clicar em "Visit Site" para continuar
- Ou criar conta para remover o aviso

### 3. Manter ngrok Rodando

O ngrok precisa estar rodando enquanto você testa no Lovable. Deixe ambos abertos:
- Terminal 1: Flask (`python wsgi.py`)
- Terminal 2: ngrok (`ngrok http 5000`)

---

## 🧪 Testar

### 1. Testar URL do ngrok

No navegador, acesse:
```
https://sua-url-ngrok.ngrok-free.app/api/v1/test
```

Deve retornar:
```json
{"success": true, "message": "API está funcionando!"}
```

### 2. Testar Login

```bash
curl -X POST https://sua-url-ngrok.ngrok-free.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SUA_SENHA_AQUI"}'
```

### 3. Usar no Lovable

No Lovable, configure:
- **URL Base**: `https://sua-url-ngrok.ngrok-free.app/api/v1`
- **Login**: `POST /auth/login`
- **Headers**: `Content-Type: application/json`

---

## 📋 Checklist

- [ ] ngrok instalado
- [ ] Flask rodando em `localhost:5000`
- [ ] ngrok rodando (`ngrok http 5000`)
- [ ] URL do ngrok copiada
- [ ] Testar `/api/v1/test` no navegador
- [ ] Configurar URL no Lovable
- [ ] Testar login no Lovable

---

## 🔄 Alternativa: Usar Render (Produção)

Se preferir não usar ngrok, você pode:

1. Fazer deploy do Flask no Render
2. Usar a URL do Render no Lovable:
   ```
   https://seu-app.onrender.com/api/v1
   ```

**Vantagens:**
- URL fixa
- Sem precisar ngrok
- Disponível 24/7

**Desvantagens:**
- Precisa fazer deploy
- Pode ter custos (plano gratuito tem limitações)

---

## 💡 Dica

Para facilitar, você pode criar um script:

```bash
#!/bin/bash
# start_ngrok.sh

# Iniciar Flask em background
python wsgi.py &
FLASK_PID=$!

# Aguardar Flask iniciar
sleep 3

# Iniciar ngrok
ngrok http 5000

# Quando ngrok parar, parar Flask também
kill $FLASK_PID
```

---

## 🆘 Troubleshooting

### Erro: "command not found: ngrok"
- Instale o ngrok (veja seção Instalação)

### Erro: "tunnel session failed"
- Verifique se o Flask está rodando na porta 5000
- Verifique se a porta não está em uso

### URL não funciona
- Verifique se ngrok está rodando
- Verifique se Flask está rodando
- Teste a URL no navegador primeiro

### CORS ainda dando erro
- Reinicie o Flask após configurar ngrok
- Verifique se os headers CORS estão sendo enviados

---

## ✅ Resumo Rápido

1. **Instalar**: `wget ... && tar -xzf ... && sudo mv ngrok /usr/local/bin/`
2. **Iniciar Flask**: `python wsgi.py` (Terminal 1)
3. **Iniciar ngrok**: `ngrok http 5000` (Terminal 2)
4. **Copiar URL**: `https://xxxx.ngrok-free.app`
5. **Usar no Lovable**: `https://xxxx.ngrok-free.app/api/v1`

Pronto! Agora o Lovable pode acessar sua API local.

