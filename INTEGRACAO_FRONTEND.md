# Integração Frontend React com API REST

Este documento explica como integrar o frontend React (criado no Lovable) com a API REST do sistema.

## Estrutura

O frontend está localizado em `frontend_lovable/connect-dashboard-main/` e é um projeto React + TypeScript + Vite.

## Configuração

### 1. Instalar Dependências

```bash
cd frontend_lovable/connect-dashboard-main
npm install
```

### 2. Configurar URL da API

Crie um arquivo `.env` na raiz do projeto frontend:

```bash
cd frontend_lovable/connect-dashboard-main
cp .env.example .env
```

Edite o `.env` e configure a URL da API:

**Para desenvolvimento local:**
```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

**Para usar com ngrok:**
```env
VITE_API_BASE_URL=https://seu-subdominio.ngrok-free.app/api/v1
```

**Para produção:**
```env
VITE_API_BASE_URL=https://seu-dominio.com/api/v1
```

### 3. Iniciar o Servidor Flask (Backend)

Em um terminal:

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor Flask
python wsgi.py
# ou
flask run
```

O servidor Flask deve estar rodando na porta 5000.

### 4. Iniciar o Frontend

Em outro terminal:

```bash
cd frontend_lovable/connect-dashboard-main
npm run dev
```

O frontend estará disponível em `http://localhost:8080` (porta configurada no `vite.config.ts`).

## Funcionalidades Integradas

### ✅ Autenticação
- Login via API (`/api/v1/auth/login`)
- Verificação de autenticação (`/api/v1/auth/me`)
- Logout

### ✅ Dashboard
- Estatísticas gerais (`/api/v1/dashboard/stats`)
- Total de alunos, professores, pagamentos pendentes
- Receita mensal

### ✅ Alunos
- Listagem de alunos (`/api/v1/alunos`)
- Busca por nome ou telefone
- Filtros por status

### ✅ Professores
- Listagem de professores (`/api/v1/professores`)
- Visualização de especialidades

### ✅ Pagamentos
- Listagem de pagamentos (`/api/v1/pagamentos`)
- Filtros por status (pendente, pago, atrasado)
- Visualização de valores e datas

## Compatibilidade de Dados

A API foi ajustada para retornar os campos esperados pelo frontend:

### Alunos
- `status`: "ativo", "inativo" ou "pendente" (derivado de `ativo` e `aprovado`)
- `email`: Campo vazio (não existe no modelo, mas frontend espera)
- `created_at`: Data de cadastro

### Professores
- `status`: "ativo" ou "inativo" (derivado de `ativo`)
- `email`: Campo vazio (não existe no modelo, mas frontend espera)
- `especialidade`: String derivada das modalidades do professor

### Pagamentos
- `valor`: Alias de `valor_pago` (campo esperado pelo frontend)
- `data_vencimento`: Calculado a partir do aluno e mês/ano de referência
- `status`: "pago", "pendente" ou "atrasado" (mapeado de "aprovado", "pendente", "rejeitado")

## Testando a Integração

1. **Inicie o backend:**
   ```bash
   python wsgi.py
   ```

2. **Inicie o frontend:**
   ```bash
   cd frontend_lovable/connect-dashboard-main
   npm run dev
   ```

3. **Acesse o frontend:**
   - Abra `http://localhost:8080`
   - Faça login com as credenciais que você configurou

4. **Verifique as páginas:**
   - Dashboard: Deve mostrar estatísticas
   - Alunos: Deve listar os alunos cadastrados
   - Professores: Deve listar os professores
   - Pagamentos: Deve listar os pagamentos

## Troubleshooting

### Erro de CORS
Se houver erros de CORS, verifique se o Flask-CORS está configurado corretamente no backend.

### Erro 401 (Não autenticado)
- Verifique se fez login corretamente
- Verifique se o token está sendo salvo no localStorage
- Verifique se o token está sendo enviado no header `Authorization`

### Erro de conexão
- Verifique se o backend está rodando na porta 5000
- Verifique se a URL no `.env` está correta
- Verifique se não há firewall bloqueando a conexão

### Dados não aparecem
- Verifique o console do navegador para erros
- Verifique a aba Network no DevTools para ver as requisições
- Verifique se a API está retornando dados corretamente

## Próximos Passos

- [ ] Adicionar funcionalidade de criar/editar alunos
- [ ] Adicionar funcionalidade de criar/editar professores
- [ ] Adicionar funcionalidade de gerenciar pagamentos
- [ ] Melhorar tratamento de erros
- [ ] Adicionar loading states mais elaborados
- [ ] Adicionar validação de formulários

