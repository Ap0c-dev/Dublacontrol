"""
Script para criar a tabela horarios_professor e adicionar coluna modalidade
Compatível com PostgreSQL e SQLite
Execute este script uma vez para atualizar o banco de dados de produção
"""
from app import create_app
from app.models.professor import db
from sqlalchemy import text, inspect

def criar_tabela_horarios_professor():
    app = create_app()
    with app.app_context():
        try:
            # Detectar tipo de banco de dados
            inspector = inspect(db.engine)
            is_postgresql = db.engine.dialect.name == 'postgresql'
            
            # Verificar se a tabela já existe
            tabela_existe = 'horarios_professor' in inspector.get_table_names()
            
            if tabela_existe:
                print("✓ Tabela 'horarios_professor' já existe.")
                
                # Verificar se a coluna modalidade existe
                colunas = [col['name'] for col in inspector.get_columns('horarios_professor')]
                coluna_modalidade_existe = 'modalidade' in colunas
                
                if coluna_modalidade_existe:
                    print("✓ Coluna 'modalidade' já existe na tabela 'horarios_professor'.")
                    return
                else:
                    print("Adicionando coluna 'modalidade' na tabela 'horarios_professor'...")
                    if is_postgresql:
                        # PostgreSQL
                        db.session.execute(text("""
                            ALTER TABLE horarios_professor 
                            ADD COLUMN modalidade VARCHAR(50) DEFAULT 'dublagem_presencial' NOT NULL
                        """))
                    else:
                        # SQLite
                        db.session.execute(text("""
                            ALTER TABLE horarios_professor 
                            ADD COLUMN modalidade VARCHAR(50) DEFAULT 'dublagem_presencial' NOT NULL
                        """))
                    
                    # Atualizar horários existentes com modalidade padrão
                    print("Atualizando modalidades dos horários existentes...")
                    if is_postgresql:
                        # Para PostgreSQL, tentar inferir a modalidade baseado no professor
                        db.session.execute(text("""
                            UPDATE horarios_professor 
                            SET modalidade = CASE
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.dublagem_presencial = true
                                ) THEN 'dublagem_presencial'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.dublagem_online = true
                                ) THEN 'dublagem_online'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.teatro_presencial = true
                                ) THEN 'teatro_presencial'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.teatro_online = true
                                ) THEN 'teatro_online'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.locucao = true
                                ) THEN 'locucao'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.musical = true
                                ) THEN 'musical'
                                ELSE 'dublagem_presencial'
                            END
                        """))
                    else:
                        # SQLite - usar 1 em vez de true
                        db.session.execute(text("""
                            UPDATE horarios_professor 
                            SET modalidade = CASE
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.dublagem_presencial = 1
                                ) THEN 'dublagem_presencial'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.dublagem_online = 1
                                ) THEN 'dublagem_online'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.teatro_presencial = 1
                                ) THEN 'teatro_presencial'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.teatro_online = 1
                                ) THEN 'teatro_online'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.locucao = 1
                                ) THEN 'locucao'
                                WHEN EXISTS (
                                    SELECT 1 FROM professores p 
                                    WHERE p.id = horarios_professor.professor_id 
                                    AND p.musical = 1
                                ) THEN 'musical'
                                ELSE 'dublagem_presencial'
                            END
                        """))
                    
                    db.session.commit()
                    print("✓ Coluna 'modalidade' adicionada com sucesso!")
                    print("NOTA: Revise os horários existentes e atualize as modalidades manualmente se necessário.")
                    return
            else:
                # Criar a tabela completa
                print("Criando tabela 'horarios_professor'...")
                if is_postgresql:
                    # PostgreSQL
                    db.session.execute(text("""
                        CREATE TABLE horarios_professor (
                            id SERIAL PRIMARY KEY,
                            professor_id INTEGER NOT NULL,
                            dia_semana VARCHAR(20) NOT NULL,
                            horario_aula VARCHAR(50) NOT NULL,
                            modalidade VARCHAR(50) NOT NULL DEFAULT 'dublagem_presencial',
                            idade_minima INTEGER,
                            idade_maxima INTEGER,
                            CONSTRAINT fk_professor FOREIGN KEY (professor_id) 
                                REFERENCES professores(id) ON DELETE CASCADE
                        )
                    """))
                else:
                    # SQLite
                    db.session.execute(text("""
                        CREATE TABLE horarios_professor (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            professor_id INTEGER NOT NULL,
                            dia_semana VARCHAR(20) NOT NULL,
                            horario_aula VARCHAR(50) NOT NULL,
                            modalidade VARCHAR(50) NOT NULL DEFAULT 'dublagem_presencial',
                            idade_minima INTEGER,
                            idade_maxima INTEGER,
                            FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE
                        )
                    """))
                
                db.session.commit()
                print("✓ Tabela 'horarios_professor' criada com sucesso!")
                print("✓ Coluna 'modalidade' incluída na criação da tabela.")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar tabela/coluna: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    criar_tabela_horarios_professor()

