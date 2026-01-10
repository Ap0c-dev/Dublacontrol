# Proposta de Melhorias no Dashboard - Análises Avançadas

## 📊 Análises Sugeridas

### 1. **Análise de Distribuição de Alunos**
- **Por Modalidade**: Gráfico de pizza/barra mostrando quantos alunos estão em cada modalidade (Dublagem Online, Presencial, Teatro, etc.)
- **Por Professor**: Gráfico mostrando distribuição de alunos por professor
- **Por Região/Cidade**: Mapa de calor ou gráfico mostrando origem geográfica dos alunos
- **Por Idade**: Distribuição etária (faixas: 0-10, 11-15, 16-20, 21-30, 31+)

### 2. **Análise de Receita**
- **Receita por Modalidade**: Qual modalidade gera mais receita
- **Receita por Professor**: Performance financeira de cada professor
- **Receita por Região**: Análise geográfica da receita
- **Ticket Médio**: Valor médio por aluno (soma de todas modalidades)
- **Receita Projetada**: Estimativa baseada em matrículas ativas

### 3. **Análise de Pagamentos**
- **Status de Pagamentos**: Pizza mostrando % aprovados, pendentes, rejeitados
- **Taxa de Inadimplência**: % de alunos atrasados vs total
- **Evolução de Status**: Gráfico de linha mostrando tendência de pagamentos ao longo do tempo
- **Pagamentos por Forma**: Distribuição (PIX, Boleto, etc.)

### 4. **Análise de Professores**
- **Retenção de Alunos por Professor**: % de alunos que continuam ativos vs que saíram
- **Taxa de Evasão por Professor**: % de alunos que encerraram matrícula com cada professor
- **Número de Alunos Ativos**: Quantos alunos ativos cada professor tem atualmente
- **Receita Gerada por Professor**: Total de receita mensal gerada por cada professor
- **Tempo Médio de Permanência**: Quantos meses em média os alunos ficam com cada professor
- **Taxa de Crescimento**: Evolução do número de alunos por professor ao longo do tempo
- **Performance Comparativa**: Ranking de professores por diferentes métricas
- **Taxa de Inadimplência por Professor**: % de alunos atrasados de cada professor
- **Modalidades por Professor**: Distribuição de modalidades que cada professor leciona

### 5. **Análise de Performance Geral**
- **Taxa de Conversão da Lista de Espera**: % de alunos que foram efetivados
- **Tempo Médio na Lista de Espera**: Quantos dias em média até efetivação
- **Taxa de Retenção Geral**: % de alunos que continuam ativos após X meses
- **Taxa de Evasão Geral**: % de alunos que saíram nos últimos meses

### 6. **Análise Temporal**
- **Horários Mais Populares**: Gráfico mostrando distribuição de horários de aula
- **Dias da Semana Mais Procurados**: Qual dia tem mais alunos
- **Sazonalidade**: Padrões de matrícula ao longo do ano

### 7. **Análise Comparativa**
- **Mês a Mês**: Comparação de métricas entre meses
- **Ano a Ano**: Comparação com mesmo período do ano anterior
- **Meta vs Realizado**: Se houver metas, mostrar progresso

## 🎨 Estrutura Proposta do Dashboard

### Opção 1: Dashboard com Tabs/Abas (Recomendado)
```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                              │
├─────────────────────────────────────────────────────────┤
│  [Visão Geral] [Alunos] [Professores] [Receita] [Pagamentos] [Análises] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Cards de │ │ Métricas │ │ Gráficos  │ │ Ações    │ │
│  │ Resumo   │ │ Principais│ │ Principais│ │ Rápidas  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                          │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Gráfico de Evolução  │ │ Distribuição         │     │
│  │ de Alunos            │ │ por Modalidade       │     │
│  └──────────────────────┘ └──────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Opção 2: Dashboard em Grid com Seções Colapsáveis
```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                              │
├─────────────────────────────────────────────────────────┤
│  📊 Métricas Principais (4 cards)                      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │
│  │      │ │      │ │      │ │      │                 │
│  └──────┘ └──────┘ └──────┘ └──────┘                 │
│                                                          │
│  ▼ Análise de Alunos                                    │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Evolução Mensal      │ │ Distribuição         │     │
│  │ (Últimos 12 meses)    │ │ por Modalidade       │     │
│  └──────────────────────┘ └──────────────────────┘     │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Por Professor        │ │ Por Região/Cidade    │     │
│  └──────────────────────┘ └──────────────────────┘     │
│                                                          │
│  ▼ Análise de Receita                                    │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Faturamento Mensal   │ │ Receita por          │     │
│  │ (Últimos 12 meses)   │ │ Modalidade           │     │
│  └──────────────────────┘ └──────────────────────┘     │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Receita por Professor│ │ Ticket Médio         │     │
│  └──────────────────────┘ └──────────────────────┘     │
│                                                          │
│  ▼ Análise de Professores                                │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Retenção de Alunos   │ │ Taxa de Evasão       │     │
│  │ por Professor        │ │ por Professor        │     │
│  └──────────────────────┘ └──────────────────────┘     │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Alunos Ativos        │ │ Receita por          │     │
│  │ por Professor        │ │ Professor             │     │
│  └──────────────────────┘ └──────────────────────┘     │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Tempo Médio de       │ │ Performance          │     │
│  │ Permanência          │ │ Comparativa          │     │
│  └──────────────────────┘ └──────────────────────┘     │
│                                                          │
│  ▼ Análise de Pagamentos                                 │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Status de Pagamentos │ │ Taxa de              │     │
│  │ (Pizza)              │ │ Inadimplência        │     │
│  └──────────────────────┘ └──────────────────────┘     │
│                                                          │
│  ▼ Performance Geral                                     │
│  ┌──────────────────────┐ ┌──────────────────────┐     │
│  │ Conversão Lista      │ │ Taxa de Retenção     │     │
│  │ de Espera            │ │ Geral                │     │
│  └──────────────────────┘ └──────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Implementação Sugerida

### Fase 1: Estrutura Base (Prioridade Alta)
1. ✅ Reorganizar dashboard com tabs/seções
2. ✅ Adicionar gráfico de distribuição por modalidade
3. ✅ Adicionar gráfico de receita por modalidade
4. ✅ Adicionar gráfico de status de pagamentos

### Fase 2: Análises Geográficas (Prioridade Média)
1. ✅ Distribuição por região/cidade
2. ✅ Receita por região

### Fase 3: Análises de Performance (Prioridade Média)
1. ✅ Taxa de conversão da lista de espera
2. ✅ Taxa de retenção/evasão
3. ✅ Análise de horários e dias da semana

### Fase 4: Análises Comparativas (Prioridade Baixa)
1. ✅ Comparação mês a mês
2. ✅ Comparação ano a ano
3. ✅ Projeções e metas

## 📋 Endpoints Necessários

### Backend (app/api/routes.py)
1. `/api/dashboard/distribuicao-modalidades` - Distribuição de alunos por modalidade
2. `/api/dashboard/distribuicao-professores` - Distribuição de alunos por professor
3. `/api/dashboard/distribuicao-regioes` - Distribuição por região/cidade
4. `/api/dashboard/distribuicao-idades` - Distribuição por faixa etária
5. `/api/dashboard/receita-modalidades` - Receita por modalidade
6. `/api/dashboard/receita-professores` - Receita por professor
7. `/api/dashboard/status-pagamentos` - Status de pagamentos (aprovados/pendentes/rejeitados)
8. `/api/dashboard/taxa-inadimplencia` - Taxa de inadimplência
9. `/api/dashboard/conversao-lista-espera` - Taxa de conversão da lista de espera
10. `/api/dashboard/horarios-populares` - Horários e dias mais populares
11. `/api/dashboard/ticket-medio` - Ticket médio por aluno

### Backend - Análises de Professores (NOVO)
12. `/api/dashboard/professores/retencao` - Retenção de alunos por professor
13. `/api/dashboard/professores/evasao` - Taxa de evasão por professor
14. `/api/dashboard/professores/alunos-ativos` - Número de alunos ativos por professor
15. `/api/dashboard/professores/receita` - Receita gerada por professor
16. `/api/dashboard/professores/tempo-permanencia` - Tempo médio de permanência
17. `/api/dashboard/professores/crescimento` - Evolução de alunos por professor
18. `/api/dashboard/professores/performance` - Performance comparativa entre professores
19. `/api/dashboard/professores/inadimplencia` - Taxa de inadimplência por professor
20. `/api/dashboard/professores/modalidades` - Modalidades lecionadas por professor

## 🎯 Benefícios

1. **Visão 360°**: Entender completamente o negócio
2. **Tomada de Decisão**: Dados para decisões estratégicas
3. **Identificar Oportunidades**: Ver onde há potencial de crescimento
4. **Otimização**: Identificar problemas (ex: alta evasão em uma modalidade)
5. **Profissionalismo**: Dashboard moderno e completo

## 💡 Sugestões de UX

1. **Filtros de Período**: Permitir filtrar análises por período (último mês, trimestre, ano)
2. **Exportação**: Botão para exportar gráficos/dados em PDF/Excel
3. **Drill-down**: Clicar em um gráfico para ver detalhes
4. **Comparação**: Toggle para comparar períodos
5. **Responsivo**: Funcionar bem em mobile/tablet

