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
    
    # Datas de início e encerramento da matrícula
    data_inicio = db.Column(db.Date, nullable=True)  # Data de início das aulas
    data_encerramento = db.Column(db.Date, nullable=True)  # Data de encerramento da matrícula (preenchida na exclusão)
    
    # Dia da semana e horário da aula (vinculados ao horário do professor)
    dia_semana = db.Column(db.String(20), nullable=True)  # Ex: "Segunda-feira"
    horario_aula = db.Column(db.String(50), nullable=True)  # Ex: "17:00 às 19:00"
    
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
            'data_matricula': self.data_matricula.isoformat() if self.data_matricula else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_encerramento': self.data_encerramento.isoformat() if self.data_encerramento else None,
            'dia_semana': self.dia_semana,
            'horario_aula': self.horario_aula
        }

