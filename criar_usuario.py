#!/usr/bin/env python3
"""
Script para criar usuários admin e gerente
Uso: python criar_usuario.py [role] [username] [senha]
     ou
     ROLE=admin USERNAME=admin PASSWORD=senha123 python criar_usuario.py
     
Roles disponíveis: admin, gerente, professor, aluno
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

def criar_usuario(role=None, username=None, senha=None):
    """Cria ou atualiza um usuário com role específica"""
    # Validar role
    roles_validos = ['admin', 'gerente', 'professor', 'aluno']
    
    # Obter role de argumentos ou variáveis de ambiente
    if not role:
        role = os.environ.get('ROLE', 'admin').lower()
    
    if role not in roles_validos:
        print(f"❌ Role inválido: {role}")
        print(f"Roles válidos: {', '.join(roles_validos)}")
        sys.exit(1)
    
    # Obter username e senha de argumentos ou variáveis de ambiente
    if not username:
        username = os.environ.get('USERNAME') or os.environ.get('ADMIN_USERNAME')
        if not username:
            username = role  # Usar o role como username padrão
    
    if not senha:
        senha = os.environ.get('PASSWORD') or os.environ.get('ADMIN_PASSWORD')
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
                # Atualizar senha e role
                usuario.set_password(senha)
                usuario.role = role
                usuario.ativo = True
                print(f"✓ Usuário '{username}' atualizado com sucesso!")
                print(f"  Role: {role}")
            else:
                # Criar novo usuário
                usuario = Usuario(
                    username=username,
                    email=f'{username}@voxen.com',
                    role=role,
                    ativo=True
                )
                usuario.set_password(senha)
                db.session.add(usuario)
                print(f"✓ Usuário '{username}' criado com sucesso!")
                print(f"  Role: {role}")
            
            db.session.commit()
            print(f"\n{'='*50}")
            print(f"✓ Credenciais de acesso:")
            print(f"  Username: {username}")
            print(f"  Senha: {senha}")
            print(f"  Role: {role}")
            print(f"  Email: {usuario.email}")
            print(f"{'='*50}")
            print(f"\n⚠️  IMPORTANTE: Anote essas credenciais em local seguro!")
            print(f"⚠️  A senha não será exibida novamente.\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Erro ao criar/atualizar usuário: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    # Obter role, username e senha dos argumentos da linha de comando
    role = sys.argv[1] if len(sys.argv) > 1 else None
    username = sys.argv[2] if len(sys.argv) > 2 else None
    senha = sys.argv[3] if len(sys.argv) > 3 else None
    
    criar_usuario(role, username, senha)

