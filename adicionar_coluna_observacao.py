#!/usr/bin/env python3
"""
Script para adicionar a coluna 'observacao' na tabela 'alunos'
Execute este script para atualizar o banco de dados.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def adicionar_coluna_observacao():
    """Adiciona a coluna observacao na tabela alunos se ela não existir"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            if db.engine.url.drivername == 'sqlite':
                # SQLite
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM pragma_table_info('alunos') 
                    WHERE name = 'observacao'
                """))
                existe = result.scalar() > 0
            else:
                # PostgreSQL
                result = db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = 'alunos' AND column_name = 'observacao'
                """))
                existe = result.scalar() > 0
            
            if existe:
                print("✅ A coluna 'observacao' já existe na tabela 'alunos'")
                return
            
            # Adicionar a coluna
            if db.engine.url.drivername == 'sqlite':
                # SQLite
                db.session.execute(text("""
                    ALTER TABLE alunos 
                    ADD COLUMN observacao TEXT
                """))
            else:
                # PostgreSQL
                db.session.execute(text("""
                    ALTER TABLE alunos 
                    ADD COLUMN observacao TEXT
                """))
            
            db.session.commit()
            print("✅ Coluna 'observacao' adicionada com sucesso na tabela 'alunos'")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao adicionar coluna 'observacao': {e}")
            raise

if __name__ == '__main__':
    print("🔄 Adicionando coluna 'observacao' na tabela 'alunos'...")
    adicionar_coluna_observacao()
    print("✅ Migração concluída!")

