from app.models.professor import db
from datetime import datetime, date

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    nome_responsavel = db.Column(db.String(200), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    
    # Endereço - campos separados
    rua = db.Column(db.String(200), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    pais = db.Column(db.String(100), nullable=True)
    
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'nome_responsavel': self.nome_responsavel,
            'telefone_responsavel': self.telefone_responsavel,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'idade': self.idade,
            'rua': self.rua,
            'numero': self.numero,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'pais': self.pais,
            'dublagem_online': self.dublagem_online,
            'dublagem_presencial': self.dublagem_presencial,
            'teatro_online': self.teatro_online,
            'teatro_presencial': self.teatro_presencial,
            'locucao': self.locucao,
            'teatro_tv_cinema': self.teatro_tv_cinema,
            'musical': self.musical,
            'professores_por_curso': self.get_professores_por_curso(),
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

