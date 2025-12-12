from app.models.professor import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='aluno')  # 'admin', 'aluno' ou 'professor'
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=True)  # Vincula usuário professor ao registro Professor
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    ultimo_acesso = db.Column(db.DateTime, nullable=True)
    
    # Relacionamento com Professor
    professor = db.relationship('Professor', backref='usuario', foreign_keys=[professor_id])
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == 'admin'
    
    def is_aluno(self):
        """Verifica se o usuário é aluno"""
        return self.role == 'aluno'
    
    def is_professor(self):
        """Verifica se o usuário é professor"""
        return self.role == 'professor'
    
    def get_professor(self):
        """Retorna o objeto Professor associado ao usuário (se for professor)"""
        if self.is_professor() and self.professor_id:
            from app.models.professor import Professor
            return Professor.query.get(self.professor_id)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None
        }

