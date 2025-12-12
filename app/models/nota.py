from app.models.professor import db
from datetime import datetime

class Nota(db.Model):
    """Modelo para armazenar notas dos alunos"""
    __tablename__ = 'notas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matriculas.id'), nullable=True)  # Opcional: vincular à matrícula específica
    
    # Tipo de curso (para referência rápida)
    tipo_curso = db.Column(db.String(50), nullable=False)
    
    # Dados da nota
    valor = db.Column(db.Float, nullable=False)  # Valor da nota (0.0 a 10.0 ou outro sistema)
    observacao = db.Column(db.Text, nullable=True)  # Observações sobre a avaliação
    data_avaliacao = db.Column(db.Date, nullable=False)  # Data em que a avaliação foi aplicada
    tipo_avaliacao = db.Column(db.String(100), nullable=True)  # Ex: "Prova", "Trabalho", "Apresentação", etc.
    
    # Metadados
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    cadastrado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Quem cadastrou a nota
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref='notas')
    professor = db.relationship('Professor', backref='notas')
    matricula = db.relationship('Matricula', backref='notas')
    usuario_cadastro = db.relationship('Usuario', foreign_keys=[cadastrado_por])
    
    def __repr__(self):
        return f'<Nota {self.id} - Aluno: {self.aluno_id} - Valor: {self.valor}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome if self.aluno else None,
            'professor_id': self.professor_id,
            'professor_nome': self.professor.nome if self.professor else None,
            'matricula_id': self.matricula_id,
            'tipo_curso': self.tipo_curso,
            'valor': float(self.valor),
            'observacao': self.observacao,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'tipo_avaliacao': self.tipo_avaliacao,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'cadastrado_por': self.cadastrado_por
        }

