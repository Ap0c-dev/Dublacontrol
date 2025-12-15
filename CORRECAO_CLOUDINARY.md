# Correção do Erro "Must supply api_key"

## Problema
O erro ocorria porque as variáveis de ambiente do Cloudinary não estavam sendo carregadas corretamente.

## Solução Implementada

### 1. Arquivo .env criado
O arquivo `.env` foi criado na raiz do projeto com as credenciais:
```
CLOUDINARY_CLOUD_NAME=docvxvt4v
CLOUDINARY_API_KEY=456143563259539
CLOUDINARY_API_SECRET=2Pa5SBVCTrGlFpKmFJGaX86vc9Y
```

### 2. python-dotenv adicionado
- Adicionado `python-dotenv>=1.0.0` ao `requirements.txt`
- Configurado carregamento automático do `.env` no `app/__init__.py`

### 3. Configuração do Cloudinary melhorada
- Cloudinary agora é configurado diretamente nas rotas antes do upload
- Adicionada validação para verificar se as credenciais estão presentes
- Mensagens de erro mais claras

## Como Aplicar a Correção

### 1. Instalar python-dotenv (se ainda não instalado)
```bash
pip install python-dotenv
```

Ou instalar todas as dependências:
```bash
pip install -r requirements.txt
```

### 2. Verificar se o arquivo .env existe
```bash
cat .env
```

Deve mostrar:
```
CLOUDINARY_CLOUD_NAME=docvxvt4v
CLOUDINARY_API_KEY=456143563259539
CLOUDINARY_API_SECRET=2Pa5SBVCTrGlFpKmFJGaX86vc9Y
```

### 3. Reiniciar a aplicação
```bash
# Parar a aplicação (Ctrl+C) e iniciar novamente
python wsgi.py
# ou
flask run
```

## Para Render (Produção)

No painel do Render, adicione as variáveis de ambiente:
- `CLOUDINARY_CLOUD_NAME`: `docvxvt4v`
- `CLOUDINARY_API_KEY`: `456143563259539`
- `CLOUDINARY_API_SECRET`: `2Pa5SBVCTrGlFpKmFJGaX86vc9Y`

**⚠️ IMPORTANTE**: O arquivo `.env` está no `.gitignore` e não será commitado. No Render, use as variáveis de ambiente do painel.

## Verificação

Após reiniciar, você deve ver no console:
```
✓ Arquivo .env carregado: /caminho/para/.env
```

Se o upload ainda não funcionar, verifique:
1. Se o arquivo `.env` existe na raiz do projeto
2. Se as credenciais estão corretas
3. Se a aplicação foi reiniciada após criar o `.env`

