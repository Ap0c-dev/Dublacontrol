# Configuração para Lovable - Guia Rápido

## ✅ API REST Pronta!

A API REST está funcionando e pronta para ser usada no Lovable.

---

## 🔗 URL Base da API

**Local (Desenvolvimento):**
```
http://localhost:5000/api/v1
```

**Produção (Render):**
```
https://seu-app.onrender.com/api/v1
```

---

## 📋 Endpoints Disponíveis

### Autenticação
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Informações do usuário atual

### Alunos
- `GET /api/v1/alunos` - Lista alunos (com filtros)
- `GET /api/v1/alunos/<id>` - Detalhes de um aluno

### Professores
- `GET /api/v1/professores` - Lista professores

### Pagamentos
- `GET /api/v1/pagamentos` - Lista pagamentos (com filtros)

### Dashboard
- `GET /api/v1/dashboard/stats` - Estatísticas gerais

---

## 🚀 Como Configurar no Lovable

### 1. Configurar URL Base da API

No Lovable, configure a URL base da API:

**Para desenvolvimento local:**
```
http://localhost:5000/api/v1
```

**Para produção:**
```
https://seu-app.onrender.com/api/v1
```

### 2. Autenticação

#### Opção A: Usar Sessão (Mais Simples para Teste)

1. Faça login primeiro via navegador: `http://localhost:5000/login`
2. O Lovable usará os cookies de sessão automaticamente

#### Opção B: Usar Token (Recomendado para Produção)

1. Faça login via API:
```javascript
const response = await fetch('http://localhost:5000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'SUA_SENHA_AQUI'
  })
});

const data = await response.json();
const token = data.token; // Guardar este token
```

2. Use o token em todas as requisições:
```javascript
fetch('http://localhost:5000/api/v1/alunos', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### 3. Exemplo de Requisição no Lovable

```javascript
// Listar alunos
const alunos = await fetch('http://localhost:5000/api/v1/alunos', {
  credentials: 'include' // Para usar cookies de sessão
}).then(r => r.json());

// Dashboard stats
const stats = await fetch('http://localhost:5000/api/v1/dashboard/stats', {
  credentials: 'include'
}).then(r => r.json());
```

---

## 🔧 Configurações Importantes

### CORS

O CORS já está configurado para permitir requisições do Lovable. Se precisar ajustar:

**No arquivo `app/__init__.py`:**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Em produção, especificar domínios do Lovable
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Para Produção

Quando for para produção, ajuste o `origins` para permitir apenas o domínio do Lovable:

```python
"origins": ["https://seu-app.lovable.app"]  # Domínio do seu app Lovable
```

---

## 📝 Formato das Respostas

### Sucesso
```json
{
  "success": true,
  "data": [...],
  "count": 10
}
```

### Erro
```json
{
  "error": "Mensagem de erro",
  "message": "Detalhes adicionais"
}
```

---

## 🧪 Testar no Lovable

### 1. Criar Componente de Login

```javascript
async function handleLogin(username, password) {
  const response = await fetch('http://localhost:5000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Salvar token
    localStorage.setItem('token', data.token);
    // Redirecionar ou atualizar estado
  }
}
```

### 2. Criar Lista de Alunos

```javascript
async function fetchAlunos() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:5000/api/v1/alunos', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.data; // Array de alunos
}
```

### 3. Criar Dashboard

```javascript
async function fetchStats() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:5000/api/v1/dashboard/stats', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.data; // { total_alunos, total_professores, ... }
}
```

---

## ⚠️ Importante

### Desenvolvimento Local

Se o Lovable estiver rodando em `localhost:3000` (ou outra porta), o CORS já está configurado para permitir.

### Produção

1. **Backend no Render**: Certifique-se de que a URL está correta
2. **CORS**: Ajuste `origins` para o domínio do Lovable
3. **HTTPS**: Use HTTPS em produção

---

## 🔍 Troubleshooting

### Erro: "Failed to fetch"
- Verifique se o Flask está rodando
- Verifique se a URL está correta
- Verifique CORS (deve estar configurado)

### Erro: "Não autenticado"
- Faça login primeiro
- Verifique se o token está sendo enviado
- Verifique se está usando `credentials: 'include'` para sessão

### Erro: "CORS error"
- Instale Flask-CORS: `pip install Flask-CORS`
- Reinicie a aplicação
- Verifique se os headers CORS estão sendo enviados

---

## ✅ Checklist para Lovable

- [ ] Flask rodando em `http://localhost:5000`
- [ ] Rota `/api/v1/test` funcionando
- [ ] CORS configurado
- [ ] URL base configurada no Lovable: `http://localhost:5000/api/v1`
- [ ] Testar login via API
- [ ] Testar listar alunos
- [ ] Testar dashboard stats

---

## 🎯 Próximos Passos

1. **No Lovable**: Configure a URL base da API
2. **Teste Login**: Crie um componente de login
3. **Teste Listagem**: Crie uma página para listar alunos
4. **Teste Dashboard**: Crie um dashboard com estatísticas

Tudo está pronto! A API está funcionando e pronta para uso no Lovable.

