from app.models.professor import db
from datetime import datetime, date

class Pagamento(db.Model):
    """Modelo para armazenar pagamentos e comprovantes dos alunos"""
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    
    # Referência do pagamento
    mes_referencia = db.Column(db.Integer, nullable=False)  # 1-12 (janeiro a dezembro)
    ano_referencia = db.Column(db.Integer, nullable=False)  # Ex: 2024
    
    # Dados do pagamento
    valor_pago = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=False)  # Data em que o aluno fez o pagamento
    
    # Comprovante
    url_comprovante = db.Column(db.String(500), nullable=True)  # URL do comprovante no Cloudinary
    public_id = db.Column(db.String(200), nullable=True)  # ID público do Cloudinary para gerenciamento
    
    # Status do pagamento
    status = db.Column(db.String(20), default='pendente', nullable=False)  # pendente, aprovado, rejeitado
    
    # Observações
    observacoes = db.Column(db.Text, nullable=True)
    observacoes_admin = db.Column(db.Text, nullable=True)  # Observações do admin ao aprovar/rejeitar
    
    # Controle
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    aprovado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Admin que aprovou
    data_aprovacao = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref='pagamentos')
    aprovador = db.relationship('Usuario', foreign_keys=[aprovado_por])
    
    def __repr__(self):
        return f'<Pagamento {self.id} - Aluno {self.aluno_id} - {self.mes_referencia}/{self.ano_referencia}>'
    
    def get_mes_nome(self):
        """Retorna o nome do mês em português"""
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(self.mes_referencia, '')
    
    def get_status_label(self):
        """Retorna o label do status em português"""
        labels = {
            'pendente': 'Pendente',
            'aprovado': 'Aprovado',
            'rejeitado': 'Rejeitado'
        }
        return labels.get(self.status, self.status)
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        classes = {
            'pendente': 'warning',
            'aprovado': 'success',
            'rejeitado': 'danger'
        }
        return classes.get(self.status, 'secondary')
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome if self.aluno else None,
            'mes_referencia': self.mes_referencia,
            'ano_referencia': self.ano_referencia,
            'mes_nome': self.get_mes_nome(),
            'valor_pago': float(self.valor_pago) if self.valor_pago else 0,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'url_comprovante': self.url_comprovante,
            'status': self.status,
            'status_label': self.get_status_label(),
            'observacoes': self.observacoes,
            'observacoes_admin': self.observacoes_admin,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'aprovado_por': self.aprovado_por,
            'aprovador_nome': self.aprovador.username if self.aprovador else None,
            'data_aprovacao': self.data_aprovacao.isoformat() if self.data_aprovacao else None
        }

