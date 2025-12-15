# Sistema de Pagamentos com Upload de Comprovantes

## ✅ Funcionalidades Implementadas

1. **Upload de Comprovante**
   - Alunos e professores podem enviar comprovantes de pagamento
   - Upload direto para Cloudinary (armazenamento em nuvem)
   - Validação de formato de arquivo (PNG, JPG, JPEG, GIF, PDF, WEBP)
   - Preview da imagem antes do upload

2. **Gerenciamento de Pagamentos**
   - Listagem de todos os pagamentos (apenas admin)
   - Filtros por status, aluno, mês e ano
   - Aprovação/rejeição de pagamentos
   - Visualização de comprovantes

3. **Status de Pagamento**
   - Pendente: Aguardando aprovação do admin
   - Aprovado: Pagamento confirmado
   - Rejeitado: Pagamento rejeitado (com motivo)

## 🔧 Configuração Necessária

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

#### Local (Desenvolvimento)

Crie um arquivo `.env` na raiz do projeto:

```bash
CLOUDINARY_CLOUD_NAME=docvxvt4v
CLOUDINARY_API_KEY=456143563259539
CLOUDINARY_API_SECRET=2Pa5SBVCTrGlFpKmFJGaX86vc9Y
```

#### Render (Produção)

No painel do Render, adicione as variáveis de ambiente:
- `CLOUDINARY_CLOUD_NAME`: `docvxvt4v`
- `CLOUDINARY_API_KEY`: `456143563259539`
- `CLOUDINARY_API_SECRET`: `2Pa5SBVCTrGlFpKmFJGaX86vc9Y`

**⚠️ IMPORTANTE**: As credenciais estão seguras e não serão commitadas no Git (`.env` está no `.gitignore`).

### 3. Criar Tabela no Banco de Dados

A tabela `pagamentos` será criada automaticamente na primeira execução. Se precisar criar manualmente:

```python
from app import create_app
from app.models.professor import db
from app.models.pagamento import Pagamento

app = create_app()
with app.app_context():
    db.create_all()
```

## 📋 Como Usar

### Para Alunos/Professores

1. Acesse a lista de alunos
2. Clique no botão "💰 Pagamento" ao lado do aluno
3. Preencha os dados:
   - Mês e ano de referência
   - Valor pago
   - Data do pagamento
   - Selecione o arquivo do comprovante
   - (Opcional) Adicione observações
4. Clique em "Enviar Comprovante"
5. Aguarde a aprovação do administrador

### Para Administradores

1. Acesse "💰 Pagamentos" no menu
2. Visualize todos os pagamentos pendentes
3. Use os filtros para encontrar pagamentos específicos
4. Para cada pagamento:
   - **Ver**: Visualizar o comprovante
   - **Aprovar**: Aprovar o pagamento (pode adicionar observações)
   - **Rejeitar**: Rejeitar o pagamento (obrigatório informar motivo)
   - **Deletar**: Remover o pagamento e o comprovante

## 🔒 Segurança

- ✅ Credenciais do Cloudinary armazenadas em variáveis de ambiente
- ✅ Nenhuma credencial commitada no Git
- ✅ URLs geradas são seguras (HTTPS)
- ✅ Validação de tipos de arquivo
- ✅ Limite de tamanho de arquivo (10MB)

## 📁 Estrutura de Arquivos

- `app/models/pagamento.py`: Modelo de dados
- `app/routes.py`: Rotas de pagamento (linhas 2160+)
- `templates/upload_comprovante.html`: Formulário de upload
- `templates/listar_pagamentos_aluno.html`: Lista de pagamentos do aluno
- `templates/listar_pagamentos.html`: Lista geral (admin)

## 🚀 Próximos Passos (Opcional)

1. **Notificações**: Enviar email quando pagamento for aprovado/rejeitado
2. **Relatórios**: Gerar relatórios de pagamentos por período
3. **Dashboard**: Gráficos de pagamentos aprovados/pendentes
4. **Status do Aluno**: Atualizar status do aluno automaticamente ao aprovar pagamento

## ⚠️ Notas Importantes

- Os comprovantes são armazenados no Cloudinary (plano gratuito: 25GB)
- Arquivos são organizados por aluno: `comprovantes/{aluno_id}/`
- Ao deletar um pagamento, o arquivo também é removido do Cloudinary
- Não é possível enviar múltiplos pagamentos aprovados para o mesmo mês/ano

