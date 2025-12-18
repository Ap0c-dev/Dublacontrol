from app.models.professor import db

class HorarioProfessor(db.Model):
    """Tabela para armazenar os horários de aula de cada professor"""
    __tablename__ = 'horarios_professor'
    
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)  # Ex: "Segunda-feira", "Terça-feira", etc.
    horario_aula = db.Column(db.String(50), nullable=False)  # Ex: "17:00 às 19:00", "20:00 às 22:00"
    modalidade = db.Column(db.String(50), nullable=False)  # dublagem_online, dublagem_presencial, teatro_presencial, teatro_online, locucao, teatro_tv_cinema, musical, curso_apresentador
    
    # Faixa etária permitida para este horário
    idade_minima = db.Column(db.Integer, nullable=True)  # Idade mínima permitida (ex: 8 anos)
    idade_maxima = db.Column(db.Integer, nullable=True)  # Idade máxima permitida (ex: 15 anos)
    
    # Relacionamento
    professor = db.relationship('Professor', backref='horarios')
    
    def __repr__(self):
        return f'<HorarioProfessor {self.professor_id} - {self.dia_semana} {self.horario_aula}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'professor_id': self.professor_id,
            'dia_semana': self.dia_semana,
            'horario_aula': self.horario_aula,
            'modalidade': self.modalidade,
            'idade_minima': self.idade_minima,
            'idade_maxima': self.idade_maxima
        }

