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
        env = app.config.get('ENVIRONMENT', 'dev')
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        print("=" * 60)
        print(f"AMBIENTE: {env.upper()}")
        print(f"BANCO DE DADOS: {db_path}")
        print("=" * 60)
        print("\nIniciando correção do banco de dados...")
        
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
                            dia_semana VARCHAR(50),
                            horario_aula VARCHAR(50),
                            ativo BOOLEAN DEFAULT 1 NOT NULL,
                            data_exclusao DATE,
                            motivo_exclusao VARCHAR(200),
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
                    
                    # Atualizar lista de colunas
                    columns = [col['name'] for col in inspector.get_columns('professores')]
                    
                    # Adicionar campos de exclusão lógica se não existirem
                    if 'ativo' not in columns:
                        try:
                            db.session.execute(text('ALTER TABLE professores ADD COLUMN ativo BOOLEAN DEFAULT 1'))
                            db.session.execute(text('ALTER TABLE professores ADD COLUMN data_exclusao DATE'))
                            db.session.execute(text('ALTER TABLE professores ADD COLUMN motivo_exclusao VARCHAR(200)'))
                            # Garantir que todos os registros existentes sejam marcados como ativos
                            db.session.execute(text("UPDATE professores SET ativo = 1 WHERE ativo IS NULL"))
                            db.session.commit()
                            print("✓ Campos de exclusão lógica adicionados à tabela 'professores'.")
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar campos de exclusão lógica: {e}")
                    
                    # Adicionar campos de dia da semana e horário se não existirem
                    if 'dia_semana' not in columns:
                        try:
                            db.session.execute(text('ALTER TABLE professores ADD COLUMN dia_semana VARCHAR(50)'))
                            db.session.commit()
                            print("✓ Coluna 'dia_semana' adicionada à tabela 'professores'.")
                            # Atualizar lista de colunas
                            columns = [col['name'] for col in inspector.get_columns('professores')]
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar coluna 'dia_semana': {e}")
                    
                    if 'horario_aula' not in columns:
                        try:
                            db.session.execute(text('ALTER TABLE professores ADD COLUMN horario_aula VARCHAR(50)'))
                            db.session.commit()
                            print("✓ Coluna 'horario_aula' adicionada à tabela 'professores'.")
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar coluna 'horario_aula': {e}")
            
            # 2. Verificar/Criar tabela usuarios
            print("\n=== Verificando tabela 'usuarios' ===")
            if 'usuarios' not in tables:
                print("Criando tabela 'usuarios'...")
                db.session.execute(text('''
                    CREATE TABLE usuarios (
                        id INTEGER PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'aluno',
                        professor_id INTEGER,
                        ativo BOOLEAN DEFAULT 1 NOT NULL,
                        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ultimo_acesso DATETIME,
                        FOREIGN KEY (professor_id) REFERENCES professores(id)
                    )
                '''))
                db.session.commit()
                print("✓ Tabela 'usuarios' criada.")
                
                # Criar usuário admin padrão
                from werkzeug.security import generate_password_hash
                admin_password = generate_password_hash('admin123')  # Senha padrão: admin123
                db.session.execute(text('''
                    INSERT INTO usuarios (username, email, password_hash, role, ativo)
                    VALUES ('admin', 'admin@controle-dublagem.com', :password, 'admin', 1)
                '''), {'password': admin_password})
                db.session.commit()
                print("✓ Usuário administrador padrão criado (username: admin, senha: admin123)")
            else:
                columns = [col['name'] for col in inspector.get_columns('usuarios')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Adicionar coluna professor_id se não existir
                if 'professor_id' not in columns:
                    try:
                        db.session.execute(text('ALTER TABLE usuarios ADD COLUMN professor_id INTEGER'))
                        db.session.commit()
                        print("✓ Coluna 'professor_id' adicionada à tabela 'usuarios'.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'professor_id': {e}")
                
                # Verificar se existe usuário admin
                admin_exists = db.session.execute(text("SELECT COUNT(*) FROM usuarios WHERE role = 'admin'")).scalar()
                if admin_exists == 0:
                    from werkzeug.security import generate_password_hash
                    admin_password = generate_password_hash('admin123')
                    db.session.execute(text('''
                        INSERT INTO usuarios (username, email, password_hash, role, ativo)
                        VALUES ('admin', 'admin@controle-dublagem.com', :password, 'admin', 1)
                    '''), {'password': admin_password})
                    db.session.commit()
                    print("✓ Usuário administrador padrão criado (username: admin, senha: admin123)")
                else:
                    print("✓ Tabela 'usuarios' verificada.")
            
            # 3. Recriar tabela alunos com estrutura correta
            print("\n=== Corrigindo tabela 'alunos' ===")
            if 'alunos' in tables:
                columns = [col['name'] for col in inspector.get_columns('alunos')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Verificar se tem data_vencimento (nova estrutura) ou dia_vencimento (antiga estrutura)
                tem_data_vencimento = 'data_vencimento' in columns
                tem_dia_vencimento = 'dia_vencimento' in columns
                
                # Se não tem data_vencimento mas tem dia_vencimento, precisa migrar
                if not tem_data_vencimento and tem_dia_vencimento:
                    print("Migrando 'dia_vencimento' para 'data_vencimento'...")
                    try:
                        # Adicionar coluna data_vencimento
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN data_vencimento DATE'))
                        
                        # Migrar dados: converter dia_vencimento para data_vencimento
                        db.session.execute(text('''
                            UPDATE alunos 
                            SET data_vencimento = CASE 
                                WHEN dia_vencimento IS NULL THEN date('now', '+10 days')
                                WHEN CAST(strftime('%d', 'now') AS INTEGER) <= dia_vencimento 
                                THEN date(strftime('%Y-%m', 'now') || '-' || printf('%02d', dia_vencimento))
                                ELSE date(strftime('%Y-%m', 'now', '+1 month') || '-' || printf('%02d', dia_vencimento))
                            END
                            WHERE dia_vencimento IS NOT NULL
                        '''))
                        
                        # Preencher valores nulos com data padrão (10 dias a partir de hoje)
                        db.session.execute(text("UPDATE alunos SET data_vencimento = date('now', '+10 days') WHERE data_vencimento IS NULL"))
                        
                        # Preencher dia_vencimento com valor padrão para evitar erro NOT NULL (SQLite não permite DROP COLUMN)
                        # Extrair o dia da data_vencimento para preencher dia_vencimento
                        db.session.execute(text('''
                            UPDATE alunos 
                            SET dia_vencimento = CAST(strftime('%d', data_vencimento) AS INTEGER)
                            WHERE dia_vencimento IS NULL AND data_vencimento IS NOT NULL
                        '''))
                        # Para registros sem data_vencimento, usar dia 10 como padrão
                        db.session.execute(text("UPDATE alunos SET dia_vencimento = 10 WHERE dia_vencimento IS NULL"))
                        
                        db.session.commit()
                        print("✓ Campo 'data_vencimento' adicionado e dados migrados de 'dia_vencimento'.")
                        print("⚠ Coluna 'dia_vencimento' ainda existe na tabela (SQLite não permite remover colunas). Ela será preenchida automaticamente.")
                        # Atualizar lista de colunas
                        columns = [col['name'] for col in inspector.get_columns('alunos')]
                        tem_data_vencimento = True
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao migrar 'dia_vencimento' para 'data_vencimento': {e}")
                
                # Verificar se tem a estrutura correta
                colunas_esperadas = ['id', 'nome', 'telefone', 'nome_responsavel', 'data_nascimento', 
                                    'idade', 'cidade', 'estado', 'forma_pagamento', 'data_vencimento',
                                    'ativo', 'data_exclusao', 'motivo_exclusao', 'aprovado',
                                    'dublagem_online', 'dublagem_presencial', 'teatro_online', 
                                    'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical', 'data_cadastro']
                
                # Verificar se tem data_vencimento (nova estrutura) ou dia_vencimento (antiga estrutura)
                tem_data_vencimento = 'data_vencimento' in columns
                tem_dia_vencimento = 'dia_vencimento' in columns
                tem_campos_exclusao = 'ativo' in columns
                
                # Verificar estrutura básica (sem campos de exclusão para não forçar recriação)
                tem_estrutura_basica = all(col in columns for col in ['id', 'nome', 'dublagem_online', 'dublagem_presencial', 'forma_pagamento', 'data_vencimento'])
                
                # Adicionar campos de exclusão lógica se não existirem (antes de verificar estrutura completa)
                if not tem_campos_exclusao:
                    try:
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN ativo BOOLEAN DEFAULT 1'))
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN data_exclusao DATE'))
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN motivo_exclusao VARCHAR(200)'))
                        # Garantir que todos os registros existentes sejam marcados como ativos
                        db.session.execute(text("UPDATE alunos SET ativo = 1 WHERE ativo IS NULL"))
                        db.session.commit()
                        print("✓ Campos de exclusão lógica adicionados à tabela 'alunos'.")
                        # Atualizar lista de colunas
                        columns = [col['name'] for col in inspector.get_columns('alunos')]
                        tem_campos_exclusao = True
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar campos de exclusão lógica: {e}")
                
                # Adicionar campo aprovado se não existir
                if 'aprovado' not in columns:
                    try:
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN aprovado BOOLEAN DEFAULT 1'))
                        # Garantir que todos os registros existentes sejam marcados como aprovados
                        db.session.execute(text("UPDATE alunos SET aprovado = 1 WHERE aprovado IS NULL"))
                        db.session.commit()
                        print("✓ Campo 'aprovado' adicionado à tabela 'alunos'.")
                        # Atualizar lista de colunas
                        columns = [col['name'] for col in inspector.get_columns('alunos')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar campo 'aprovado': {e}")
                
                # Verificar se o campo 'lembrar_aniversario' existe
                if 'lembrar_aniversario' not in columns:
                    try:
                        db.session.execute(text('ALTER TABLE alunos ADD COLUMN lembrar_aniversario BOOLEAN DEFAULT 0 NOT NULL'))
                        db.session.commit()
                        print("✓ Campo 'lembrar_aniversario' adicionado à tabela 'alunos'.")
                        # Atualizar lista de colunas
                        columns = [col['name'] for col in inspector.get_columns('alunos')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar campo 'lembrar_aniversario': {e}")
                
                tem_estrutura_correta = all(col in columns for col in ['id', 'nome', 'dublagem_online', 'dublagem_presencial', 'forma_pagamento', 'data_vencimento', 'ativo'])
                
                if not tem_estrutura_basica:
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
                            lembrar_aniversario BOOLEAN DEFAULT 0 NOT NULL,
                            cidade VARCHAR(100) NOT NULL,
                            estado VARCHAR(2) NOT NULL,
                            forma_pagamento VARCHAR(50) NOT NULL,
                            data_vencimento DATE NOT NULL,
                            ativo BOOLEAN DEFAULT 1 NOT NULL,
                            data_exclusao DATE,
                            motivo_exclusao VARCHAR(200),
                            aprovado BOOLEAN DEFAULT 1 NOT NULL,
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
                    # Adicionar campos que faltam
                    # Nota: SQLite não suporta NOT NULL em ALTER TABLE ADD COLUMN sem DEFAULT
                    # Então adicionamos como nullable primeiro, depois atualizamos valores e depois tornamos NOT NULL
                    campos_faltantes = {
                        'cidade': ('VARCHAR(100)', '""'),
                        'estado': ('VARCHAR(2)', '""'),
                        'forma_pagamento': ('VARCHAR(50)', '"PIX"'),
                        'data_vencimento': ('DATE', None),
                        'ativo': ('BOOLEAN DEFAULT 1', None),
                        'data_exclusao': ('DATE', None),
                        'motivo_exclusao': ('VARCHAR(200)', None),
                        'musical': ('BOOLEAN DEFAULT 0', None),
                        'telefone_responsavel': ('VARCHAR(20)', None)
                    }
                    
                    # Adicionar campos de exclusão lógica se não existirem
                    if not tem_campos_exclusao:
                        try:
                            db.session.execute(text('ALTER TABLE alunos ADD COLUMN ativo BOOLEAN DEFAULT 1 NOT NULL'))
                            db.session.execute(text('ALTER TABLE alunos ADD COLUMN data_exclusao DATE'))
                            db.session.execute(text('ALTER TABLE alunos ADD COLUMN motivo_exclusao VARCHAR(200)'))
                            # Garantir que todos os registros existentes sejam marcados como ativos
                            db.session.execute(text("UPDATE alunos SET ativo = 1 WHERE ativo IS NULL"))
                            db.session.commit()
                            print("✓ Campos de exclusão lógica adicionados à tabela 'alunos'.")
                            columns = [col['name'] for col in inspector.get_columns('alunos')]
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar campos de exclusão lógica: {e}")
                    
                    # Se dia_vencimento existe, precisamos migrar para data_vencimento
                    if 'dia_vencimento' in columns and 'data_vencimento' not in columns:
                        try:
                            # Adicionar coluna data_vencimento
                            db.session.execute(text('ALTER TABLE alunos ADD COLUMN data_vencimento DATE'))
                            
                            # Migrar dados: converter dia_vencimento para data_vencimento
                            # Usar o dia do mês atual ou próximo mês se já passou
                            from datetime import date, timedelta
                            hoje = date.today()
                            
                            db.session.execute(text('''
                                UPDATE alunos 
                                SET data_vencimento = CASE 
                                    WHEN dia_vencimento IS NULL THEN date('now', '+10 days')
                                    WHEN CAST(strftime('%d', 'now') AS INTEGER) <= dia_vencimento 
                                    THEN date(strftime('%Y-%m', 'now') || '-' || printf('%02d', dia_vencimento))
                                    ELSE date(strftime('%Y-%m', 'now', '+1 month') || '-' || printf('%02d', dia_vencimento))
                                END
                                WHERE dia_vencimento IS NOT NULL
                            '''))
                            
                            # Preencher valores nulos com data padrão (10 dias a partir de hoje)
                            db.session.execute(text("UPDATE alunos SET data_vencimento = date('now', '+10 days') WHERE data_vencimento IS NULL"))
                            
                            db.session.commit()
                            print("✓ Campo 'data_vencimento' adicionado e dados migrados de 'dia_vencimento'.")
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao migrar 'dia_vencimento' para 'data_vencimento': {e}")
                    
                    # Atualizar lista de colunas após adicionar campos de exclusão
                    columns = [col['name'] for col in inspector.get_columns('alunos')]
                    
                    for campo, (tipo, valor_default) in campos_faltantes.items():
                        if campo not in columns:
                            try:
                                if valor_default is not None:
                                    # Adicionar coluna com valor padrão
                                    db.session.execute(text(f'ALTER TABLE alunos ADD COLUMN {campo} {tipo} DEFAULT {valor_default}'))
                                    # Atualizar registros existentes que possam estar NULL
                                    if campo in ['cidade', 'estado', 'forma_pagamento']:
                                        if campo == 'cidade':
                                            db.session.execute(text(f"UPDATE alunos SET {campo} = '' WHERE {campo} IS NULL"))
                                        elif campo == 'estado':
                                            db.session.execute(text(f"UPDATE alunos SET {campo} = '' WHERE {campo} IS NULL"))
                                        elif campo == 'forma_pagamento':
                                            db.session.execute(text(f"UPDATE alunos SET {campo} = 'PIX' WHERE {campo} IS NULL"))
                                elif campo == 'data_vencimento':
                                    # Adicionar coluna data_vencimento e preencher com data padrão
                                    db.session.execute(text('ALTER TABLE alunos ADD COLUMN data_vencimento DATE'))
                                    db.session.execute(text("UPDATE alunos SET data_vencimento = date('now', '+10 days') WHERE data_vencimento IS NULL"))
                                elif campo == 'ativo':
                                    # Adicionar coluna ativo com valor padrão
                                    db.session.execute(text('ALTER TABLE alunos ADD COLUMN ativo BOOLEAN DEFAULT 1 NOT NULL'))
                                    db.session.execute(text("UPDATE alunos SET ativo = 1 WHERE ativo IS NULL"))
                                else:
                                    # Adicionar coluna sem valor padrão (nullable)
                                    db.session.execute(text(f'ALTER TABLE alunos ADD COLUMN {campo} {tipo}'))
                                db.session.commit()
                                print(f"✓ Campo '{campo}' adicionado.")
                            except Exception as e:
                                db.session.rollback()
                                print(f"✗ Erro ao adicionar '{campo}': {e}")
                    
                    # Remover campos antigos se existirem (após migração)
                    if 'data_vencimento' in columns and 'dia_vencimento' in columns:
                        print("⚠ Campo antigo 'data_vencimento' ainda existe. Considere removê-lo após verificar a migração.")
                    
                    for campo, tipo in campos_faltantes.items():
                        if campo not in columns:
                            try:
                                db.session.execute(text(f'ALTER TABLE alunos ADD COLUMN {campo} {tipo}'))
                                db.session.commit()
                                print(f"✓ Campo '{campo}' adicionado.")
                            except Exception as e:
                                db.session.rollback()
                                print(f"✗ Erro ao adicionar '{campo}': {e}")
                    
                    # Remover campos antigos de endereço se existirem
                    campos_antigos = ['rua', 'numero', 'bairro', 'pais']
                    for campo_antigo in campos_antigos:
                        if campo_antigo in columns:
                            try:
                                # SQLite não suporta DROP COLUMN diretamente, então vamos apenas avisar
                                print(f"⚠ Campo antigo '{campo_antigo}' ainda existe na tabela. Para removê-lo, será necessário recriar a tabela.")
                            except Exception as e:
                                print(f"✗ Erro ao verificar campo antigo '{campo_antigo}': {e}")
            else:
                print("Criando tabela 'alunos'...")
                db.create_all()
                print("✓ Tabela 'alunos' criada.")
            
            # 4. Criar/verificar tabela matriculas
            print("\n=== Verificando tabela 'matriculas' ===")
            if 'matriculas' not in tables:
                print("Criando tabela 'matriculas'...")
                db.session.execute(text('''
                    CREATE TABLE matriculas (
                        id INTEGER PRIMARY KEY,
                        aluno_id INTEGER NOT NULL,
                        professor_id INTEGER NOT NULL,
                        tipo_curso VARCHAR(50) NOT NULL,
                        valor_mensalidade REAL,
                        data_inicio DATE,
                        data_encerramento DATE,
                        dia_semana VARCHAR(20),
                        horario_aula VARCHAR(50),
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
                
                # Verificar se a coluna valor_mensalidade existe
                if 'valor_mensalidade' not in columns:
                    print("Adicionando coluna 'valor_mensalidade'...")
                    try:
                        db.session.execute(text('ALTER TABLE matriculas ADD COLUMN valor_mensalidade REAL'))
                        db.session.commit()
                        print("✓ Coluna 'valor_mensalidade' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('matriculas')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'valor_mensalidade': {e}")
                else:
                    print("✓ Coluna 'valor_mensalidade' já existe.")
                
                # Verificar se a coluna data_inicio existe
                if 'data_inicio' not in columns:
                    print("Adicionando coluna 'data_inicio'...")
                    try:
                        db.session.execute(text('ALTER TABLE matriculas ADD COLUMN data_inicio DATE'))
                        db.session.commit()
                        print("✓ Coluna 'data_inicio' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('matriculas')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'data_inicio': {e}")
                else:
                    print("✓ Coluna 'data_inicio' já existe.")
                
                # Verificar se a coluna data_encerramento existe
                if 'data_encerramento' not in columns:
                    print("Adicionando coluna 'data_encerramento'...")
                    try:
                        db.session.execute(text('ALTER TABLE matriculas ADD COLUMN data_encerramento DATE'))
                        db.session.commit()
                        print("✓ Coluna 'data_encerramento' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('matriculas')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'data_encerramento': {e}")
                else:
                    print("✓ Coluna 'data_encerramento' já existe.")
                
                # Verificar se a coluna dia_semana existe
                if 'dia_semana' not in columns:
                    print("Adicionando coluna 'dia_semana'...")
                    try:
                        db.session.execute(text('ALTER TABLE matriculas ADD COLUMN dia_semana VARCHAR(20)'))
                        db.session.commit()
                        print("✓ Coluna 'dia_semana' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('matriculas')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'dia_semana': {e}")
                else:
                    print("✓ Coluna 'dia_semana' já existe.")
                
                # Verificar se a coluna horario_aula existe
                if 'horario_aula' not in columns:
                    print("Adicionando coluna 'horario_aula'...")
                    try:
                        db.session.execute(text('ALTER TABLE matriculas ADD COLUMN horario_aula VARCHAR(50)'))
                        db.session.commit()
                        print("✓ Coluna 'horario_aula' adicionada.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'horario_aula': {e}")
                else:
                    print("✓ Coluna 'horario_aula' já existe.")
                
                print("✓ Tabela 'matriculas' verificada.")
            
            # 5. Criar/verificar tabela horarios_professor
            print("\n=== Verificando tabela 'horarios_professor' ===")
            if 'horarios_professor' not in tables:
                print("Criando tabela 'horarios_professor'...")
                db.session.execute(text('''
                    CREATE TABLE horarios_professor (
                        id INTEGER PRIMARY KEY,
                        professor_id INTEGER NOT NULL,
                        dia_semana VARCHAR(20) NOT NULL,
                        horario_aula VARCHAR(50) NOT NULL,
                        idade_minima INTEGER,
                        idade_maxima INTEGER,
                        FOREIGN KEY (professor_id) REFERENCES professores(id)
                    )
                '''))
                db.session.commit()
                print("✓ Tabela 'horarios_professor' criada.")
            else:
                columns = [col['name'] for col in inspector.get_columns('horarios_professor')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Verificar se tem horario_aula (estrutura atual)
                if 'horario_aula' not in columns:
                    # Se tem horario_inicio e horario_termino, adicionar horario_aula
                    if 'horario_inicio' in columns and 'horario_termino' in columns:
                        print("Adicionando coluna 'horario_aula'...")
                        try:
                            db.session.execute(text('ALTER TABLE horarios_professor ADD COLUMN horario_aula VARCHAR(50)'))
                            # Migrar dados: concatenar horario_inicio e horario_termino
                            db.session.execute(text('''
                                UPDATE horarios_professor 
                                SET horario_aula = horario_inicio || ' às ' || horario_termino
                                WHERE horario_aula IS NULL
                            '''))
                            db.session.commit()
                            print("✓ Coluna 'horario_aula' adicionada e dados migrados.")
                            columns = [col['name'] for col in inspector.get_columns('horarios_professor')]
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar coluna 'horario_aula': {e}")
                
                # Adicionar colunas de idade se não existirem
                if 'idade_minima' not in columns:
                    print("Adicionando coluna 'idade_minima'...")
                    try:
                        db.session.execute(text('ALTER TABLE horarios_professor ADD COLUMN idade_minima INTEGER'))
                        db.session.commit()
                        print("✓ Coluna 'idade_minima' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('horarios_professor')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'idade_minima': {e}")
                
                if 'idade_maxima' not in columns:
                    print("Adicionando coluna 'idade_maxima'...")
                    try:
                        db.session.execute(text('ALTER TABLE horarios_professor ADD COLUMN idade_maxima INTEGER'))
                        db.session.commit()
                        print("✓ Coluna 'idade_maxima' adicionada.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'idade_maxima': {e}")
                
                print("✓ Tabela 'horarios_professor' verificada.")
            
            # 6. Criar/verificar tabela notas
            print("\n=== Verificando tabela 'notas' ===")
            if 'notas' not in tables:
                print("Criando tabela 'notas'...")
                db.session.execute(text('''
                    CREATE TABLE notas (
                        id INTEGER PRIMARY KEY,
                        aluno_id INTEGER NOT NULL,
                        professor_id INTEGER NOT NULL,
                        matricula_id INTEGER,
                        tipo_curso VARCHAR(50) NOT NULL,
                        valor REAL,
                        observacao TEXT,
                        data_avaliacao DATE NOT NULL,
                        tipo_avaliacao VARCHAR(100),
                        criterio1 REAL,
                        criterio2 REAL,
                        criterio3 REAL,
                        criterio4 REAL,
                        numero_prova INTEGER,
                        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                        cadastrado_por INTEGER,
                        FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                        FOREIGN KEY (professor_id) REFERENCES professores(id),
                        FOREIGN KEY (matricula_id) REFERENCES matriculas(id),
                        FOREIGN KEY (cadastrado_por) REFERENCES usuarios(id)
                    )
                '''))
                db.session.commit()
                print("✓ Tabela 'notas' criada.")
            else:
                columns = [col['name'] for col in inspector.get_columns('notas')]
                print(f"Colunas atuais: {', '.join(columns)}")
                
                # Verificar e adicionar campos de critérios se não existirem
                for i in range(1, 5):
                    campo = f'criterio{i}'
                    if campo not in columns:
                        print(f"Adicionando coluna '{campo}'...")
                        try:
                            db.session.execute(text(f'ALTER TABLE notas ADD COLUMN {campo} REAL'))
                            db.session.commit()
                            print(f"✓ Coluna '{campo}' adicionada.")
                            columns = [col['name'] for col in inspector.get_columns('notas')]
                        except Exception as e:
                            db.session.rollback()
                            print(f"✗ Erro ao adicionar coluna '{campo}': {e}")
                
                # Verificar e adicionar campo numero_prova se não existir
                if 'numero_prova' not in columns:
                    print("Adicionando coluna 'numero_prova'...")
                    try:
                        db.session.execute(text('ALTER TABLE notas ADD COLUMN numero_prova INTEGER'))
                        db.session.commit()
                        print("✓ Coluna 'numero_prova' adicionada.")
                        columns = [col['name'] for col in inspector.get_columns('notas')]
                    except Exception as e:
                        db.session.rollback()
                        print(f"✗ Erro ao adicionar coluna 'numero_prova': {e}")
                
                # Verificar se valor pode ser NULL (foi alterado para nullable)
                # SQLite não suporta ALTER COLUMN, então isso é apenas informativo
                
                print("✓ Tabela 'notas' verificada.")
            
            print("\n✓ Correção do banco de dados concluída com sucesso!")
            
        except Exception as e:
            print(f"\n✗ Erro durante a correção: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    corrigir_banco()

