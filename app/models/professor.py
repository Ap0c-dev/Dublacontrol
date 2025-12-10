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
    
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    
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
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

