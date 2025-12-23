#!/usr/bin/env python3
"""
Script para adicionar a coluna aluno_id na tabela usuarios
Funciona com SQLite e PostgreSQL
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models.professor import db
from sqlalchemy import text, inspect
from sqlalchemy.engine import reflection

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Detectar tipo de banco de dados
            db_uri = str(db.engine.url)
            is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
            is_sqlite = 'sqlite' in db_uri
            
            # Verificar se a coluna já existe
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('usuarios')]
            
            if 'aluno_id' in columns:
                print("✅ Coluna 'aluno_id' já existe na tabela 'usuarios'")
                return
            
            # Adicionar a coluna aluno_id
            print("🔄 Adicionando coluna 'aluno_id' na tabela 'usuarios'...")
            
            if is_postgres:
                # PostgreSQL
                db.session.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN IF NOT EXISTS aluno_id INTEGER REFERENCES alunos(id)
                """))
            elif is_sqlite:
                # SQLite - não suporta IF NOT EXISTS, então já verificamos acima
                db.session.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN aluno_id INTEGER REFERENCES alunos(id)
                """))
            else:
                # Outros bancos
                db.session.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN aluno_id INTEGER
                """))
            
            db.session.commit()
            print("✅ Coluna 'aluno_id' adicionada com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            # Se o erro for "column already exists", ignorar
            if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                print("✅ Coluna 'aluno_id' já existe (erro ignorado)")
            else:
                print(f"❌ Erro ao adicionar coluna: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)

if __name__ == '__main__':
    migrate()

