#!/usr/bin/env python3
"""
Script para corrigir a estrutura do banco de dados.
Recria as tabelas com a estrutura correta.
"""

from app import create_app
from app.models.professor import db
from sqlalchemy import inspect, text

def corrigir_banco():
    """Corrige a estrutura do banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("Iniciando correção do banco de dados...")
        
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            # 1. Corrigir tabela professores
            if 'professores' in tables:
                print("\n=== Corrigindo tabela 'professores' ===")
                columns = [col['name'] for col in inspector.get_columns('professores')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Verificar se tem colunas antigas
                tem_colunas_antigas = 'professor_dublagem' in columns or 'professor_teatro' in columns
                
                if tem_colunas_antigas:
                    print("Colunas antigas detectadas. Recriando tabela...")
                    
                    # Criar tabela temporária com estrutura correta
                    db.session.execute(text('''
                        CREATE TABLE professores_temp (
                            id INTEGER PRIMARY KEY,
                            nome VARCHAR(200) NOT NULL,
                            telefone VARCHAR(20),
                            dublagem_presencial BOOLEAN DEFAULT 0 NOT NULL,
                            dublagem_online BOOLEAN DEFAULT 0 NOT NULL,
                            teatro_presencial BOOLEAN DEFAULT 0 NOT NULL,
                            teatro_online BOOLEAN DEFAULT 0 NOT NULL,
                            musical BOOLEAN DEFAULT 0 NOT NULL,
                            locucao BOOLEAN DEFAULT 0 NOT NULL,
                            curso_apresentador BOOLEAN DEFAULT 0 NOT NULL,
                            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    '''))
                    
                    # Copiar dados existentes
                    if 'professor_dublagem' in columns and 'professor_teatro' in columns:
                        # Migrar dados das colunas antigas
                        db.session.execute(text('''
                            INSERT INTO professores_temp 
                            (id, nome, telefone, dublagem_presencial, dublagem_online, 
                             teatro_presencial, teatro_online, musical, locucao, curso_apresentador, data_cadastro)
                            SELECT 
                                id, 
                                nome, 
                                telefone,
                                CASE WHEN professor_dublagem = 1 THEN 1 ELSE 0 END as dublagem_presencial,
                                CASE WHEN professor_dublagem = 1 THEN 1 ELSE 0 END as dublagem_online,
                                CASE WHEN professor_teatro = 1 THEN 1 ELSE 0 END as teatro_presencial,
                                CASE WHEN professor_teatro = 1 THEN 1 ELSE 0 END as teatro_online,
                                COALESCE(musical, 0) as musical,
                                COALESCE(locucao, 0) as locucao,
                                COALESCE(curso_apresentador, 0) as curso_apresentador,
                                data_cadastro
                            FROM professores
                        '''))
                    else:
                        # Se já tem algumas novas colunas, copiar diretamente
                        novas_cols = ['id', 'nome', 'telefone', 'data_cadastro']
                        novas_cols.extend([col for col in ['dublagem_presencial', 'dublagem_online', 
                                                           'teatro_presencial', 'teatro_online', 
                                                           'musical', 'locucao', 'curso_apresentador'] 
                                          if col in columns])
                        
                        cols_str = ', '.join(novas_cols)
                        db.session.execute(text(f'''
                            INSERT INTO professores_temp ({cols_str})
                            SELECT {cols_str}
                            FROM professores
                        '''))
                    
                    # Remover tabela antiga e renomear
                    db.session.execute(text('DROP TABLE professores'))
                    db.session.execute(text('ALTER TABLE professores_temp RENAME TO professores'))
                    db.session.commit()
                    print("✓ Tabela 'professores' recriada com sucesso!")
                else:
                    # Apenas adicionar colunas que faltam
                    novas_colunas = {
                        'dublagem_presencial': 'BOOLEAN DEFAULT 0',
                        'dublagem_online': 'BOOLEAN DEFAULT 0',
                        'teatro_presencial': 'BOOLEAN DEFAULT 0',
                        'teatro_online': 'BOOLEAN DEFAULT 0',
                        'musical': 'BOOLEAN DEFAULT 0',
                        'locucao': 'BOOLEAN DEFAULT 0',
                        'curso_apresentador': 'BOOLEAN DEFAULT 0'
                    }
                    
                    for coluna, tipo in novas_colunas.items():
                        if coluna not in columns:
                            try:
                                db.session.execute(text(f'ALTER TABLE professores ADD COLUMN {coluna} {tipo}'))
                                db.session.commit()
                                print(f"✓ Coluna '{coluna}' adicionada.")
                            except Exception as e:
                                db.session.rollback()
                                print(f"✗ Erro ao adicionar '{coluna}': {e}")
            
            # 2. Recriar tabela alunos com estrutura correta
            print("\n=== Corrigindo tabela 'alunos' ===")
            if 'alunos' in tables:
                columns = [col['name'] for col in inspector.get_columns('alunos')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Verificar se tem a estrutura correta
                colunas_esperadas = ['id', 'nome', 'telefone', 'nome_responsavel', 'data_nascimento', 
                                    'idade', 'rua', 'numero', 'bairro', 'cidade', 'pais',
                                    'dublagem_online', 'dublagem_presencial', 'teatro_online', 
                                    'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical', 'data_cadastro']
                
                tem_estrutura_correta = all(col in columns for col in ['id', 'nome', 'dublagem_online', 'dublagem_presencial'])
                
                if not tem_estrutura_correta:
                    print("Estrutura incorreta detectada. Recriando tabela...")
                    
                    # Criar backup da tabela antiga
                    try:
                        db.session.execute(text('ALTER TABLE alunos RENAME TO alunos_backup'))
                        db.session.commit()
                        print("Tabela antiga renomeada para 'alunos_backup'")
                    except:
                        pass
                    
                    # Criar nova tabela com estrutura correta
                    db.session.execute(text('''
                        CREATE TABLE alunos (
                            id INTEGER PRIMARY KEY,
                            nome VARCHAR(200) NOT NULL,
                            telefone VARCHAR(20) NOT NULL,
                            telefone_responsavel VARCHAR(20),
                            nome_responsavel VARCHAR(200),
                            data_nascimento DATE,
                            idade INTEGER,
                            rua VARCHAR(200),
                            numero VARCHAR(20),
                            bairro VARCHAR(100),
                            cidade VARCHAR(100),
                            pais VARCHAR(100),
                            dublagem_online BOOLEAN DEFAULT 0 NOT NULL,
                            dublagem_presencial BOOLEAN DEFAULT 0 NOT NULL,
                            teatro_online BOOLEAN DEFAULT 0 NOT NULL,
                            teatro_presencial BOOLEAN DEFAULT 0 NOT NULL,
                            locucao BOOLEAN DEFAULT 0 NOT NULL,
                            teatro_tv_cinema BOOLEAN DEFAULT 0 NOT NULL,
                            musical BOOLEAN DEFAULT 0 NOT NULL,
                            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    '''))
                    db.session.commit()
                    print("✓ Tabela 'alunos' recriada com estrutura correta.")
                else:
                    # Apenas adicionar campos que faltam
                    campos_faltantes = {
                        'rua': 'VARCHAR(200)', 
                        'numero': 'VARCHAR(20)', 
                        'bairro': 'VARCHAR(100)', 
                        'cidade': 'VARCHAR(100)', 
                        'pais': 'VARCHAR(100)',
                        'musical': 'BOOLEAN DEFAULT 0',
                        'telefone_responsavel': 'VARCHAR(20)'
                    }
                    
                    for campo, tipo in campos_faltantes.items():
                        if campo not in columns:
                            try:
                                db.session.execute(text(f'ALTER TABLE alunos ADD COLUMN {campo} {tipo}'))
                                db.session.commit()
                                print(f"✓ Campo '{campo}' adicionado.")
                            except Exception as e:
                                db.session.rollback()
                                print(f"✗ Erro ao adicionar '{campo}': {e}")
            else:
                print("Criando tabela 'alunos'...")
                db.create_all()
                print("✓ Tabela 'alunos' criada.")
            
            # 3. Criar/verificar tabela matriculas
            print("\n=== Verificando tabela 'matriculas' ===")
            if 'matriculas' not in tables:
                print("Criando tabela 'matriculas'...")
                db.session.execute(text('''
                    CREATE TABLE matriculas (
                        id INTEGER PRIMARY KEY,
                        aluno_id INTEGER NOT NULL,
                        professor_id INTEGER NOT NULL,
                        tipo_curso VARCHAR(50) NOT NULL,
                        data_matricula DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                        FOREIGN KEY (professor_id) REFERENCES professores(id)
                    )
                '''))
                db.session.commit()
                print("✓ Tabela 'matriculas' criada.")
            else:
                columns = [col['name'] for col in inspector.get_columns('matriculas')]
                print(f"Colunas atuais: {', '.join(columns)}")
                print("✓ Tabela 'matriculas' já existe.")
            
            print("\n✓ Correção do banco de dados concluída com sucesso!")
            
        except Exception as e:
            print(f"\n✗ Erro durante a correção: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    corrigir_banco()

