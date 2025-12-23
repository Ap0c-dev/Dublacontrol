from app.models.professor import db
from datetime import datetime, timedelta
import secrets

class SenhaReset(db.Model):
    """Modelo para armazenar códigos de recuperação de senha"""
    __tablename__ = 'senha_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    codigo = db.Column(db.String(12), unique=True, nullable=False, index=True)  # Código de 12 caracteres
    usado = db.Column(db.Boolean, default=False, nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    data_expiracao = db.Column(db.DateTime, nullable=False)  # Expira em 24 horas
    criado_por_admin = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Admin que gerou o código
    
    # Relacionamentos
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='senha_resets')
    admin_criador = db.relationship('Usuario', foreign_keys=[criado_por_admin])
    
    @staticmethod
    def gerar_codigo():
        """Gera um código único de 12 caracteres (letras e números)"""
        caracteres = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Removido 0, O, I, 1 para evitar confusão
        return ''.join(secrets.choice(caracteres) for _ in range(12))
    
    @staticmethod
    def criar_codigo(usuario_id, criado_por_admin=None):
        """Cria um novo código de recuperação"""
        # Limpar códigos antigos não usados do mesmo usuário
        SenhaReset.query.filter_by(
            usuario_id=usuario_id,
            usado=False
        ).filter(SenhaReset.data_expiracao < datetime.now()).delete()
        
        codigo = SenhaReset.gerar_codigo()
        # Garantir que o código é único
        while SenhaReset.query.filter_by(codigo=codigo).first():
            codigo = SenhaReset.gerar_codigo()
        
        reset = SenhaReset(
            usuario_id=usuario_id,
            codigo=codigo,
            data_expiracao=datetime.now() + timedelta(hours=24),
            criado_por_admin=criado_por_admin
        )
        db.session.add(reset)
        db.session.commit()
        return reset
    
    def is_valido(self):
        """Verifica se o código ainda é válido"""
        return not self.usado and datetime.now() < self.data_expiracao
    
    def usar(self):
        """Marca o código como usado"""
        self.usado = True
        db.session.commit()
    
    def __repr__(self):
        return f'<SenhaReset {self.codigo} - Usuario {self.usuario_id}>'

