from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Professor(db.Model):
    __tablename__ = 'professores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    
    # Modalidades específicas
    dublagem_presencial = db.Column(db.Boolean, default=False, nullable=False)
    dublagem_online = db.Column(db.Boolean, default=False, nullable=False)
    teatro_presencial = db.Column(db.Boolean, default=False, nullable=False)
    teatro_online = db.Column(db.Boolean, default=False, nullable=False)
    musical = db.Column(db.Boolean, default=False, nullable=False)
    locucao = db.Column(db.Boolean, default=False, nullable=False)
    curso_apresentador = db.Column(db.Boolean, default=False, nullable=False)
    
    # Dia da semana e horário da aula
    dia_semana = db.Column(db.String(50), nullable=True)  # Ex: "Segunda, Quarta, Sexta" ou "Segunda-feira"
    horario_aula = db.Column(db.String(50), nullable=True)  # Ex: "14:00 às 16:00" ou "19:00 às 21:00"
    
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Exclusão lógica
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_exclusao = db.Column(db.Date, nullable=True)
    motivo_exclusao = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Professor {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'dublagem_presencial': self.dublagem_presencial,
            'dublagem_online': self.dublagem_online,
            'teatro_presencial': self.teatro_presencial,
            'teatro_online': self.teatro_online,
            'musical': self.musical,
            'locucao': self.locucao,
            'curso_apresentador': self.curso_apresentador,
            'dia_semana': self.dia_semana,
            'horario_aula': self.horario_aula,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo,
            'data_exclusao': self.data_exclusao.isoformat() if self.data_exclusao else None,
            'motivo_exclusao': self.motivo_exclusao
        }

