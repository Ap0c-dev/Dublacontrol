# Solução: Erro "Credenciais do Cloudinary não encontradas"

## Problema Identificado

O erro ocorria porque o arquivo `.env` estava sendo carregado **depois** do `Config` ser importado. Quando o `Config` é criado, ele lê as variáveis de ambiente, mas se o `.env` ainda não foi carregado, as variáveis ficam vazias.

## Correções Aplicadas

### 1. Ordem de Carregamento Corrigida (`app/__init__.py`)

**ANTES** (errado):
```python
from flask import Flask
from config import Config  # ← Config é importado ANTES do .env ser carregado
# ... depois carrega .env
```

**DEPOIS** (correto):
```python
import os
# Carregar .env PRIMEIRO
load_dotenv(...)
# AGORA importar Config (que vai ler as variáveis já carregadas)
from flask import Flask
from config import Config
```

### 2. Validação Melhorada (`app/routes.py`)

Agora a rota verifica as credenciais tanto nas variáveis de ambiente quanto no config do Flask, e mostra mensagens de erro mais detalhadas.

### 3. Config com Valores Padrão (`config.py`)

O `config.py` agora usa valores padrão caso as variáveis não estejam definidas.

## Como Aplicar

### 1. Reiniciar a Aplicação

**IMPORTANTE**: Você precisa reiniciar a aplicação Flask para que as mudanças tenham efeito!

```bash
# Parar a aplicação (Ctrl+C)
# Depois iniciar novamente:
python wsgi.py
# ou
flask run
```

### 2. Verificar se Funcionou

Ao iniciar, você deve ver no console:
```
✓ Arquivo .env carregado: /home/tiago/controle-dublagem/.env
```

### 3. Testar o Upload

Tente fazer upload de um comprovante novamente. Se ainda der erro, execute o script de teste:

```bash
python3 test_cloudinary_config.py
```

Este script vai verificar:
- Se o arquivo `.env` existe e está sendo carregado
- Se as variáveis estão definidas
- Se o Config está lendo as variáveis corretamente
- Se o Cloudinary pode ser configurado

## Verificação Rápida

Execute este comando para verificar se as variáveis estão sendo carregadas:

```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLOUDINARY_CLOUD_NAME:', os.environ.get('CLOUDINARY_CLOUD_NAME')); print('CLOUDINARY_API_KEY:', 'OK' if os.environ.get('CLOUDINARY_API_KEY') else 'FALTANDO')"
```

Deve mostrar:
```
CLOUDINARY_CLOUD_NAME: docvxvt4v
CLOUDINARY_API_KEY: OK
```

## Se Ainda Não Funcionar

1. **Verifique se o arquivo `.env` existe**:
   ```bash
   cat .env
   ```

2. **Verifique se python-dotenv está instalado**:
   ```bash
   pip install python-dotenv
   ```

3. **Verifique se a aplicação foi reiniciada** após as mudanças

4. **Execute o script de teste**:
   ```bash
   python3 test_cloudinary_config.py
   ```

## Para Render (Produção)

No Render, as variáveis de ambiente devem ser configuradas no painel:
- `CLOUDINARY_CLOUD_NAME`: `docvxvt4v`
- `CLOUDINARY_API_KEY`: `456143563259539`
- `CLOUDINARY_API_SECRET`: `2Pa5SBVCTrGlFpKmFJGaX86vc9Y`

O arquivo `.env` não é usado no Render, apenas as variáveis de ambiente do painel.

