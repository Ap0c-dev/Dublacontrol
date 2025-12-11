from app.models.professor import db

class Matricula(db.Model):
    """Tabela intermediária para relacionar Aluno, Professor e Curso"""
    __tablename__ = 'matriculas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    
    # Tipo de curso
    tipo_curso = db.Column(db.String(50), nullable=False)  # dublagem_online, dublagem_presencial, teatro_online, teatro_presencial, locucao, teatro_tv_cinema, musical
    
    # Valor da mensalidade para esta modalidade
    valor_mensalidade = db.Column(db.Float, nullable=True)  # Permite valores decimais (ex: 150.50)
    
    data_matricula = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref='matriculas')
    professor = db.relationship('Professor', backref='matriculas')
    
    def __repr__(self):
        return f'<Matricula {self.aluno_id} - {self.professor_id} - {self.tipo_curso}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'professor_id': self.professor_id,
            'tipo_curso': self.tipo_curso,
            'valor_mensalidade': float(self.valor_mensalidade) if self.valor_mensalidade else None,
            'professor_nome': self.professor.nome if self.professor else None,
            'data_matricula': self.data_matricula.isoformat() if self.data_matricula else None
        }

