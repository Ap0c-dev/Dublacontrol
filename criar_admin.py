#!/usr/bin/env python3
"""
Script para criar ou redefinir o usuário administrador
Uso: python criar_admin.py [username] [senha]
     ou
     ADMIN_USERNAME=admin ADMIN_PASSWORD=senha123 python criar_admin.py
"""

import sys
import os
import secrets
import string
from app import create_app
from app.models.professor import db
from app.models.usuario import Usuario

def gerar_senha_aleatoria(tamanho=12):
    """Gera uma senha aleatória segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(caracteres) for _ in range(tamanho))

def criar_admin(username=None, senha=None):
    """Cria ou atualiza o usuário administrador"""
    # Obter username e senha de argumentos ou variáveis de ambiente
    if not username:
        username = os.environ.get('ADMIN_USERNAME') or 'admin'
    
    if not senha:
        senha = os.environ.get('ADMIN_PASSWORD')
        if not senha:
            # Gerar senha aleatória se não fornecida
            senha = gerar_senha_aleatoria()
            print(f"⚠️  Nenhuma senha fornecida. Gerando senha aleatória...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se o usuário já existe
            usuario = Usuario.query.filter_by(username=username).first()
            
            if usuario:
                # Atualizar senha e garantir que é admin
                usuario.set_password(senha)
                usuario.role = 'admin'
                usuario.ativo = True
                print(f"✓ Usuário '{username}' atualizado com sucesso!")
            else:
                # Criar novo usuário admin
                usuario = Usuario(
                    username=username,
                    email=f'{username}@controle-dublagem.com',
                    role='admin',
                    ativo=True
                )
                usuario.set_password(senha)
                db.session.add(usuario)
                print(f"✓ Usuário administrador '{username}' criado com sucesso!")
            
            db.session.commit()
            print(f"\n{'='*50}")
            print(f"✓ Credenciais de acesso:")
            print(f"  Username: {username}")
            print(f"  Senha: {senha}")
            print(f"  Email: {usuario.email}")
            print(f"{'='*50}")
            print(f"\n⚠️  IMPORTANTE: Anote essas credenciais em local seguro!")
            print(f"⚠️  A senha não será exibida novamente.\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Erro ao criar/atualizar usuário admin: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    # Obter username e senha dos argumentos da linha de comando
    username = sys.argv[1] if len(sys.argv) > 1 else None
    senha = sys.argv[2] if len(sys.argv) > 2 else None
    
    criar_admin(username, senha)

