#!/usr/bin/env python3
"""
Script para adicionar as novas colunas ao banco de dados:
- experimental (em alunos)
- teatro_tv_cinema (em professores)
"""

from app import create_app
from app.models.professor import db
from sqlalchemy import inspect, text

def adicionar_colunas():
    """Adiciona as novas colunas ao banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Adicionando novas colunas ao banco de dados...")
        print("=" * 60)
        
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # 1. Adicionar coluna experimental na tabela alunos
            if 'alunos' in tables:
                columns = [col['name'] for col in inspector.get_columns('alunos')]
                print(f"\nColunas atuais em 'alunos': {', '.join(columns)}")
                
                if 'experimental' not in columns:
                    print("Adicionando coluna 'experimental' na tabela 'alunos'...")
                    try:
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN experimental BOOLEAN DEFAULT 0 NOT NULL'))
                        db.session.commit()
                        print("✓ Coluna 'experimental' adicionada com sucesso!")
                    except Exception as e:
                        db.session.rollback()
                        print(f"⚠️  Erro ao adicionar coluna 'experimental': {e}")
                        print("   (Pode ser que a coluna já exista)")
                else:
                    print("✓ Coluna 'experimental' já existe em 'alunos'")
            else:
                print("⚠️  Tabela 'alunos' não existe. Ela será criada automaticamente na próxima execução.")
            
            # 2. Adicionar coluna teatro_tv_cinema na tabela professores
            if 'professores' in tables:
                columns = [col['name'] for col in inspector.get_columns('professores')]
                print(f"\nColunas atuais em 'professores': {', '.join(columns)}")
                
                if 'teatro_tv_cinema' not in columns:
                    print("Adicionando coluna 'teatro_tv_cinema' na tabela 'professores'...")
                    try:
                        db.session.execute(text('ALTER TABLE professores ADD COLUMN teatro_tv_cinema BOOLEAN DEFAULT 0 NOT NULL'))
                        db.session.commit()
                        print("✓ Coluna 'teatro_tv_cinema' adicionada com sucesso!")
                    except Exception as e:
                        db.session.rollback()
                        print(f"⚠️  Erro ao adicionar coluna 'teatro_tv_cinema': {e}")
                        print("   (Pode ser que a coluna já exista)")
                else:
                    print("✓ Coluna 'teatro_tv_cinema' já existe em 'professores'")
            else:
                print("⚠️  Tabela 'professores' não existe. Ela será criada automaticamente na próxima execução.")
            
            # 3. Verificar se a tabela pagamentos existe (para o sistema de pagamentos)
            if 'pagamentos' not in tables:
                print("\n⚠️  Tabela 'pagamentos' não existe. Ela será criada automaticamente na próxima execução.")
            else:
                print("\n✓ Tabela 'pagamentos' já existe")
            
            print("\n" + "=" * 60)
            print("Migração concluída!")
            print("=" * 60)
            
        except Exception as e:
            import traceback
            print(f"\n✗ Erro durante a migração: {e}")
            print(traceback.format_exc())
            db.session.rollback()

if __name__ == '__main__':
    adicionar_colunas()

