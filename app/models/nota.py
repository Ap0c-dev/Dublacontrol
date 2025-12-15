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
    valor = db.Column(db.Float, nullable=True)  # Valor da nota (0.0 a 10.0) - pode ser null se usar critérios
    observacao = db.Column(db.Text, nullable=True)  # Observações sobre a avaliação
    data_avaliacao = db.Column(db.Date, nullable=False)  # Data em que a avaliação foi aplicada
    tipo_avaliacao = db.Column(db.String(100), nullable=True)  # Ex: "Prova", "Trabalho", "Apresentação", etc.
    
    # 4 Critérios de avaliação (para cursos de dublagem)
    criterio1 = db.Column(db.Float, nullable=True)  # Critério 1 (0.0 a 10.0)
    criterio2 = db.Column(db.Float, nullable=True)  # Critério 2 (0.0 a 10.0)
    criterio3 = db.Column(db.Float, nullable=True)  # Critério 3 (0.0 a 10.0)
    criterio4 = db.Column(db.Float, nullable=True)  # Critério 4 (0.0 a 10.0)
    
    # Número da prova (1 a 8 - 4 provas por ano, 8 provas no total do curso)
    numero_prova = db.Column(db.Integer, nullable=True)  # 1, 2, 3, 4, 5, 6, 7, 8
    
    def calcular_media(self):
        """Calcula a média dos 4 critérios"""
        criterios = [self.criterio1, self.criterio2, self.criterio3, self.criterio4]
        criterios_validos = [c for c in criterios if c is not None]
        if criterios_validos:
            return sum(criterios_validos) / len(criterios_validos)
        return None
    
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
            'valor': float(self.valor) if self.valor is not None else None,
            'observacao': self.observacao,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None,
            'tipo_avaliacao': self.tipo_avaliacao,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'cadastrado_por': self.cadastrado_por,
            'criterio1': float(self.criterio1) if self.criterio1 is not None else None,
            'criterio2': float(self.criterio2) if self.criterio2 is not None else None,
            'criterio3': float(self.criterio3) if self.criterio3 is not None else None,
            'criterio4': float(self.criterio4) if self.criterio4 is not None else None,
            'numero_prova': self.numero_prova,
            'media': self.calcular_media()
        }

