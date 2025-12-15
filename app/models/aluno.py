from app.models.professor import db
from datetime import datetime, date
from sqlalchemy import event
from sqlalchemy import text

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    nome_responsavel = db.Column(db.String(200), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    lembrar_aniversario = db.Column(db.Boolean, default=False, nullable=False)  # Se o aluno quer ter aniversário lembrado
    
    # Endereço - apenas cidade e estado (obrigatórios)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    
    # Forma de pagamento e vencimento
    forma_pagamento = db.Column(db.String(50), nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)  # Data de vencimento (dia/mês) - obrigatório
    dia_vencimento = db.Column(db.Integer, nullable=True)  # Campo legado - preenchido automaticamente a partir de data_vencimento
    
    # Cursos
    dublagem_online = db.Column(db.Boolean, default=False, nullable=False)
    dublagem_presencial = db.Column(db.Boolean, default=False, nullable=False)
    teatro_online = db.Column(db.Boolean, default=False, nullable=False)
    teatro_presencial = db.Column(db.Boolean, default=False, nullable=False)
    locucao = db.Column(db.Boolean, default=False, nullable=False)
    teatro_tv_cinema = db.Column(db.Boolean, default=False, nullable=False)
    musical = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relacionamento com professores através de Matricula (muitos-para-muitos)
    # Removido professor_id - agora usamos a tabela Matricula
    
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Exclusão lógica
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_exclusao = db.Column(db.Date, nullable=True)
    motivo_exclusao = db.Column(db.String(200), nullable=True)
    
    # Aprovação de cadastro
    aprovado = db.Column(db.Boolean, default=True, nullable=False)  # True = aprovado, False = pendente
    
    # Aluno experimental (aula experimental)
    experimental = db.Column(db.Boolean, default=False, nullable=False)  # True = experimental, False = efetivado
    
    def get_professores_por_curso(self):
        """Retorna um dicionário com professores por tipo de curso"""
        from app.models.matricula import Matricula
        matriculas = Matricula.query.filter_by(aluno_id=self.id).all()
        resultado = {}
        for matricula in matriculas:
            if matricula.tipo_curso not in resultado:
                resultado[matricula.tipo_curso] = []
            resultado[matricula.tipo_curso].append({
                'id': matricula.professor.id,
                'nome': matricula.professor.nome
            })
        return resultado
    
    def calcular_idade(self):
        """Calcula a idade baseada na data de nascimento"""
        if self.data_nascimento:
            today = date.today()
            idade = today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
            return idade
        return None
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'
    
    def get_total_mensalidades(self):
        """Retorna a soma de todas as mensalidades do aluno"""
        total = 0
        for matricula in self.matriculas:
            if matricula.valor_mensalidade:
                total += float(matricula.valor_mensalidade)
        return total
    
    def get_mensalidades_por_modalidade(self):
        """Retorna um dicionário com mensalidades agrupadas por modalidade"""
        resultado = {}
        for matricula in self.matriculas:
            modalidade = matricula.tipo_curso
            valor = float(matricula.valor_mensalidade) if matricula.valor_mensalidade else 0
            if modalidade not in resultado:
                resultado[modalidade] = {
                    'valor': valor,
                    'professor': matricula.professor.nome if matricula.professor else None,
                    'quantidade': 1
                }
            else:
                # Se houver múltiplas matrículas na mesma modalidade (improvável, mas possível)
                resultado[modalidade]['valor'] += valor
                resultado[modalidade]['quantidade'] += 1
        return resultado
    
    def get_mensalidade_por_modalidade(self, tipo_curso):
        """Retorna o valor da mensalidade para uma modalidade específica"""
        for matricula in self.matriculas:
            if matricula.tipo_curso == tipo_curso:
                return float(matricula.valor_mensalidade) if matricula.valor_mensalidade else 0
        return 0
    
    def get_status_vencimento(self):
        """
        Retorna o status de vencimento do aluno:
        - 'vencido': data de vencimento já passou
        - 'vence_hoje': vence hoje
        - 'vence_amanha': vence amanhã (1 dia antes)
        - 'ok': ainda não está próximo do vencimento
        """
        if not self.data_vencimento:
            return 'ok'
        
        hoje = date.today()
        data_venc = self.data_vencimento
        
        # Calcular diferença em dias
        diff_dias = (data_venc - hoje).days
        
        if diff_dias < 0:
            return 'vencido'  # Vermelho
        elif diff_dias == 0:
            return 'vence_hoje'  # Laranja
        elif diff_dias == 1:
            return 'vence_amanha'  # Verde (1 dia antes)
        else:
            return 'ok'  # Sem indicador (mais de 1 dia)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'nome_responsavel': self.nome_responsavel,
            'telefone_responsavel': self.telefone_responsavel,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'idade': self.idade,
            'cidade': self.cidade,
            'estado': self.estado,
            'forma_pagamento': self.forma_pagamento,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'dublagem_online': self.dublagem_online,
            'dublagem_presencial': self.dublagem_presencial,
            'teatro_online': self.teatro_online,
            'teatro_presencial': self.teatro_presencial,
            'locucao': self.locucao,
            'teatro_tv_cinema': self.teatro_tv_cinema,
            'musical': self.musical,
            'professores_por_curso': self.get_professores_por_curso(),
            'total_mensalidades': self.get_total_mensalidades(),
            'mensalidades_por_modalidade': self.get_mensalidades_por_modalidade(),
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo,
            'data_exclusao': self.data_exclusao.isoformat() if self.data_exclusao else None,
            'motivo_exclusao': self.motivo_exclusao
        }

# Evento para preencher dia_vencimento automaticamente (compatibilidade com banco antigo)
@event.listens_for(Aluno, 'before_insert')
def preencher_dia_vencimento(mapper, connection, target):
    """Preenche dia_vencimento com o dia extraído de data_vencimento antes de inserir"""
    if target.data_vencimento:
        target.dia_vencimento = target.data_vencimento.day

