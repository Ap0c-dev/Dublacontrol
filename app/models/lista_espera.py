from app.models.professor import db
from datetime import datetime

class ListaEspera(db.Model):
    """Modelo para alunos em lista de espera"""
    __tablename__ = 'lista_espera'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    curso = db.Column(db.String(100), nullable=True)  # Curso de interesse
    idade = db.Column(db.Integer, nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    regiao = db.Column(db.String(100), nullable=True)  # Região (ex: Zona Norte, Centro, etc.)
    estado = db.Column(db.String(2), nullable=True)
    dia_semana = db.Column(db.String(20), nullable=True)  # Dia da semana preferido
    data_pretende_entrar = db.Column(db.Date, nullable=True)  # Data que pretende entrar no curso
    nome_responsavel = db.Column(db.String(200), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    efetivado = db.Column(db.Boolean, default=False, nullable=False)  # Se foi efetivado como aluno
    data_efetivacao = db.Column(db.DateTime, nullable=True)  # Data em que foi efetivado
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=True)  # ID do aluno criado após efetivação
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'curso': self.curso,
            'idade': self.idade,
            'cidade': self.cidade,
            'regiao': self.regiao,
            'estado': self.estado,
            'dia_semana': self.dia_semana,
            'data_pretende_entrar': self.data_pretende_entrar.isoformat() if self.data_pretende_entrar else None,
            'nome_responsavel': self.nome_responsavel,
            'telefone_responsavel': self.telefone_responsavel,
            'observacao': self.observacao,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'efetivado': self.efetivado,
            'data_efetivacao': self.data_efetivacao.isoformat() if self.data_efetivacao else None,
            'aluno_id': self.aluno_id
        }
    
    def __repr__(self):
        return f'<ListaEspera {self.nome}>'

