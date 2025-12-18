"""
Script para adicionar a coluna 'modalidade' na tabela horarios_professor
Execute este script uma vez para atualizar o banco de dados existente
"""
from app import create_app
from app.models.professor import db
from sqlalchemy import text

def adicionar_coluna_modalidade():
    app = create_app()
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM pragma_table_info('horarios_professor') 
                WHERE name='modalidade'
            """))
            
            coluna_existe = result.fetchone()[0] > 0
            
            if coluna_existe:
                print("A coluna 'modalidade' já existe na tabela horarios_professor.")
                return
            
            # Adicionar coluna modalidade
            print("Adicionando coluna 'modalidade' na tabela horarios_professor...")
            db.session.execute(text("""
                ALTER TABLE horarios_professor 
                ADD COLUMN modalidade VARCHAR(50) DEFAULT 'dublagem_presencial' NOT NULL
            """))
            
            # Para horários existentes, tentar inferir a modalidade baseado no professor
            # Se não for possível, usar 'dublagem_presencial' como padrão
            print("Atualizando modalidades dos horários existentes...")
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
            print("Coluna 'modalidade' adicionada com sucesso!")
            print("NOTA: Revise os horários existentes e atualize as modalidades manualmente se necessário.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao adicionar coluna: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    adicionar_coluna_modalidade()

