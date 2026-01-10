# Como Testar Localmente

Este guia explica como rodar o sistema completo (backend + frontend) localmente para testar as novas funcionalidades.

## 📋 Pré-requisitos

1. **Python 3.10+** instalado
2. **Node.js 18+** e **npm** ou **yarn** instalados
3. **Git** (para clonar o repositório, se necessário)

## 🔧 Configuração do Backend (Flask)

### 1. Ativar o ambiente virtual

```bash
cd /home/tiago/controle-dublagem
source venv/bin/activate
```

### 2. Instalar dependências (se ainda não instalou)

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente (opcional)

Crie um arquivo `.env` na raiz do projeto se quiser configurar variáveis específicas:

```bash
# .env (opcional para desenvolvimento local)
SECRET_KEY=sua-chave-secreta-local
ENVIRONMENT=dev
DATABASE_PATH=/home/tiago
```

**Nota**: O sistema funciona sem `.env` em desenvolvimento, usando valores padrão.

### 4. Iniciar o servidor backend

```bash
python wsgi.py
```

O backend estará rodando em: **http://localhost:5000**

**Ou use o script de desenvolvimento:**

```bash
./start-dev.sh
```

## 🎨 Configuração do Frontend (React/Vite)

### 1. Navegar para a pasta do frontend

```bash
cd frontend_lovable/connect-dashboard-main
```

### 2. Instalar dependências (se ainda não instalou)

```bash
npm install
# ou
yarn install
```

### 3. Configurar URL da API (opcional)

Por padrão, o frontend tenta se conectar a `http://localhost:5000/api/v1`.

Se precisar alterar, crie um arquivo `.env` na pasta `frontend_lovable/connect-dashboard-main/`:

```bash
# .env.local
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

### 4. Iniciar o servidor de desenvolvimento

```bash
npm run dev
# ou
yarn dev
```

O frontend estará rodando em: **http://localhost:8080** (conforme configurado no vite.config.ts)

## 🚀 Testando o Dashboard com Tabs

### 1. Acessar o sistema

1. Abra o navegador em: **http://localhost:8080**
2. Faça login com suas credenciais

### 2. Navegar para o Dashboard

Após o login, você será redirecionado para o Dashboard.

### 3. Testar as Tabs

- **Visão Geral**: Mostra os cards de estatísticas principais
- **Professores**: Clique nesta tab para carregar a tabela de performance de professores
  - A tabela mostra métricas como retenção, evasão, alunos que mudaram de professor, etc.
- **Alunos**: Acesso ao gráfico de evolução
- **Receita**: Acesso ao gráfico de faturamento
- **Pagamentos**: Acesso à lista de pagamentos

### 4. Verificar a lógica de evasão

A lógica de evasão considera:
- Matrículas explicitamente encerradas
- Alunos que mudaram de professor (têm matrícula ativa com outro professor)

## 🔍 Verificando se está funcionando

### Backend

Verifique se o endpoint está respondendo:

```bash
curl http://localhost:5000/api/v1/dashboard/professores/performance \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Frontend

1. Abra o **Console do Navegador** (F12)
2. Vá para a tab **Network**
3. Clique na tab **Professores** no Dashboard
4. Verifique se a requisição para `/dashboard/professores/performance` é feita com sucesso

## 🐛 Troubleshooting

### Backend não inicia

- Verifique se o ambiente virtual está ativado: `which python` deve apontar para `venv/bin/python`
- Verifique se todas as dependências estão instaladas: `pip list`
- Verifique se a porta 5000 está livre: `lsof -i :5000`

### Frontend não conecta ao backend

- Verifique se o backend está rodando em `http://localhost:5000`
- Verifique a variável `VITE_API_BASE_URL` no `.env.local`
- Verifique o console do navegador para erros de CORS

### Erro de CORS

Se aparecer erro de CORS, o Flask-CORS já está configurado. Se persistir:

1. Verifique se `Flask-CORS` está instalado: `pip show flask-cors`
2. Verifique se o backend está permitindo requisições do frontend (já configurado no código)

### Dados não aparecem

- Verifique se há dados no banco de dados
- Verifique se você está logado com um usuário que tem permissão
- Verifique o console do navegador para erros

## 📝 Estrutura de Portas

- **Backend (Flask)**: `http://localhost:5000`
- **Frontend (Vite)**: `http://localhost:8080`

## 🎯 Próximos Passos

Após testar localmente:

1. Verifique se todas as funcionalidades estão funcionando
2. Teste com dados reais do banco
3. Se tudo estiver OK, faça commit e push para produção

## 💡 Dicas

- Use **dois terminais**: um para o backend e outro para o frontend
- O Vite tem **Hot Module Replacement (HMR)**: mudanças no frontend são refletidas automaticamente
- O Flask em modo debug também recarrega automaticamente quando você salva arquivos Python

