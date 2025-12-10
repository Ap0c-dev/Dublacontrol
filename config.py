import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Banco de dados - Render usa DATABASE_URL ou podemos usar SQLite local
    if os.environ.get('DATABASE_URL'):
        # Render PostgreSQL ou outro banco via DATABASE_URL
        # Render usa postgres:// mas SQLAlchemy precisa postgresql://
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # SQLite local (desenvolvimento ou se não houver DATABASE_URL)
        # No Render, se não houver DATABASE_URL, usar diretório temporário
        if os.environ.get('RENDER'):
            # Render - usar diretório temporário (dados serão perdidos ao reiniciar)
            import tempfile
            DB_PATH = os.path.join(tempfile.gettempdir(), 'controle_dublagem.db')
        else:
            # Desenvolvimento local
            DB_PATH = os.environ.get('DATABASE_PATH') or '/home/tiago/banco_lucy'
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

