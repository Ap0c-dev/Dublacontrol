#!/usr/bin/env python3
"""
Script de migração manual para atualizar a estrutura do banco de dados.
Execute este script para atualizar as tabelas com as novas colunas de modalidades.
"""

from app import create_app
from app.models.professor import db
from sqlalchemy import inspect, text

def migrar_banco():
    """Executa a migração do banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("Iniciando migração do banco de dados...")
        
        try:
            inspector = inspect(db.engine)
            
            if 'professores' not in inspector.get_table_names():
                print("Tabela 'professores' não existe. Criando...")
                db.create_all()
                print("Tabela criada com sucesso!")
                return
            
            columns = [col['name'] for col in inspector.get_columns('professores')]
            print(f"Colunas atuais: {', '.join(columns)}")
            
            # Adicionar novas colunas se não existirem
            novas_colunas = {
                'dublagem_presencial': 'BOOLEAN DEFAULT 0',
                'dublagem_online': 'BOOLEAN DEFAULT 0',
                'teatro_presencial': 'BOOLEAN DEFAULT 0',
                'teatro_online': 'BOOLEAN DEFAULT 0',
                'musical': 'BOOLEAN DEFAULT 0',
                'locucao': 'BOOLEAN DEFAULT 0',
                'curso_apresentador': 'BOOLEAN DEFAULT 0'
            }
            
            colunas_adicionadas = []
            for coluna, tipo in novas_colunas.items():
                if coluna not in columns:
                    try:
                        db.session.execute(text(f'ALTER TABLE professores ADD COLUMN {coluna} {tipo}'))
                        db.session.commit()
                        colunas_adicionadas.append(coluna)
                        print(f"✓ Coluna '{coluna}' adicionada com sucesso.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna '{coluna}': {e}")
                else:
                    print(f"  Coluna '{coluna}' já existe.")
            
            if colunas_adicionadas:
                print(f"\n{len(colunas_adicionadas)} coluna(s) adicionada(s) com sucesso!")
            
            # Migrar dados das colunas antigas para as novas (se existirem)
            if 'professor_dublagem' in columns:
                try:
                    resultado = db.session.execute(text('''
                        UPDATE professores 
                        SET dublagem_presencial = 1, dublagem_online = 1 
                        WHERE professor_dublagem = 1
                    '''))
                    db.session.commit()
                    linhas_afetadas = resultado.rowcount
                    print(f"✓ Dados de dublagem migrados: {linhas_afetadas} registro(s) atualizado(s).")
                except Exception as e:
                    db.session.rollback()
                    print(f"✗ Erro ao migrar dados de dublagem: {e}")
            
            if 'professor_teatro' in columns:
                try:
                    resultado = db.session.execute(text('''
                        UPDATE professores 
                        SET teatro_presencial = 1, teatro_online = 1 
                        WHERE professor_teatro = 1
                    '''))
                    db.session.commit()
                    linhas_afetadas = resultado.rowcount
                    print(f"✓ Dados de teatro migrados: {linhas_afetadas} registro(s) atualizado(s).")
                except Exception as e:
                    db.session.rollback()
                    print(f"✗ Erro ao migrar dados de teatro: {e}")
            
            print("\nMigração concluída!")
            
        except Exception as e:
            print(f"Erro durante a migração: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrar_banco()

