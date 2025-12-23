#!/usr/bin/env python3
"""
Script para adicionar a coluna aluno_id na tabela usuarios
Execute este script após atualizar o modelo Usuario
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models.professor import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('usuarios') 
                WHERE name = 'aluno_id'
            """))
            count = result.fetchone()[0]
            
            if count > 0:
                print("✅ Coluna 'aluno_id' já existe na tabela 'usuarios'")
                return
            
            # Adicionar a coluna aluno_id
            print("🔄 Adicionando coluna 'aluno_id' na tabela 'usuarios'...")
            db.session.execute(text("""
                ALTER TABLE usuarios 
                ADD COLUMN aluno_id INTEGER REFERENCES alunos(id)
            """))
            db.session.commit()
            print("✅ Coluna 'aluno_id' adicionada com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao adicionar coluna: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate()

