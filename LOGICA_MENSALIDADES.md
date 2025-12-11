# Lógica de Armazenamento de Mensalidades

## Como Funciona Atualmente

### Estrutura de Dados

Cada **matrícula** (relacionamento entre Aluno + Professor + Modalidade) armazena:
- `aluno_id`: ID do aluno
- `professor_id`: ID do professor
- `tipo_curso`: Modalidade (dublagem_online, dublagem_presencial, etc.)
- `valor_mensalidade`: Valor da mensalidade **para aquela modalidade específica**

### Exemplo Prático

**Cenário**: Aluno "João Silva" está matriculado em 3 modalidades:
1. Dublagem Online - Professor "Maria" - R$ 150,00
2. Teatro Presencial - Professor "Pedro" - R$ 200,00
3. Musical - Professor "Ana" - R$ 180,00

**No Banco de Dados**:
```
Tabela: matriculas

id | aluno_id | professor_id | tipo_curso          | valor_mensalidade
1  | 1        | 5            | dublagem_online     | 150.00
2  | 1        | 8            | teatro_presencial   | 200.00
3  | 1        | 12           | musical             | 180.00
```

**Resultado**: 3 registros separados, cada um com seu próprio valor.

## Vantagens desta Abordagem

### ✅ Análises por Modalidade
```python
# Total de receita por modalidade
SELECT tipo_curso, SUM(valor_mensalidade) 
FROM matriculas 
GROUP BY tipo_curso
```

### ✅ Total de Mensalidades por Aluno
```python
# Soma de todas as mensalidades de um aluno
SELECT aluno_id, SUM(valor_mensalidade) 
FROM matriculas 
WHERE aluno_id = 1
```

### ✅ Análises por Professor
```python
# Receita por professor
SELECT professor_id, SUM(valor_mensalidade) 
FROM matriculas 
GROUP BY professor_id
```

### ✅ Relatórios Detalhados
- Valor médio por modalidade
- Alunos que pagam mais (soma de todas modalidades)
- Professores que geram mais receita
- Modalidades mais lucrativas
- Análise temporal (por mês/ano)

## Métodos Auxiliares Criados

### No Modelo `Aluno`:

1. **`get_total_mensalidades()`**
   - Retorna a soma de todas as mensalidades do aluno
   - Exemplo: Se tem 3 modalidades (R$150 + R$200 + R$180) = R$ 530,00

2. **`get_mensalidades_por_modalidade()`**
   - Retorna um dicionário com valores por modalidade
   - Exemplo: `{'dublagem_online': {'valor': 150.00, 'professor': 'Maria'}, ...}`

3. **`get_mensalidade_por_modalidade(tipo_curso)`**
   - Retorna o valor de uma modalidade específica
   - Exemplo: `get_mensalidade_por_modalidade('dublagem_online')` = 150.00

## Consultas Úteis para Dashboard

### 1. Total de Receita Mensal
```python
from app.models.matricula import Matricula
from sqlalchemy import func

total = db.session.query(func.sum(Matricula.valor_mensalidade)).scalar()
```

### 2. Receita por Modalidade
```python
receita_por_modalidade = db.session.query(
    Matricula.tipo_curso,
    func.sum(Matricula.valor_mensalidade)
).group_by(Matricula.tipo_curso).all()
```

### 3. Top 10 Alunos por Valor Total
```python
top_alunos = db.session.query(
    Aluno.nome,
    func.sum(Matricula.valor_mensalidade).label('total')
).join(Matricula).group_by(Aluno.id).order_by(func.sum(Matricula.valor_mensalidade).desc()).limit(10).all()
```

### 4. Receita por Professor
```python
receita_professor = db.session.query(
    Professor.nome,
    func.sum(Matricula.valor_mensalidade)
).join(Matricula).group_by(Professor.id).all()
```

### 5. Média de Mensalidade por Modalidade
```python
media_por_modalidade = db.session.query(
    Matricula.tipo_curso,
    func.avg(Matricula.valor_mensalidade)
).group_by(Matricula.tipo_curso).all()
```

## Resumo

✅ **Cada modalidade tem seu próprio valor** (não somado, não dividido)
✅ **Valores são armazenados separadamente** na tabela `matriculas`
✅ **Permite análises detalhadas** por modalidade, aluno, professor
✅ **Facilita relatórios** e dashboards futuros
✅ **Flexível** para diferentes tipos de consultas

Esta estrutura é a **ideal** para análises de dados e dashboards!

