import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Determinar ambiente (dev ou prd)
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev').lower()  # 'dev' ou 'prd'
    
    # Banco de dados
    if os.environ.get('DATABASE_URL'):
        # Render PostgreSQL ou outro banco via DATABASE_URL (produção)
        # Render usa postgres:// mas SQLAlchemy precisa postgresql://
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
        ENVIRONMENT = 'prd'  # Se tem DATABASE_URL, está em produção
    else:
        # SQLite local - separar dev e prd
        BASE_DB_PATH = os.environ.get('DATABASE_PATH') or '/home/tiago'
        
        if ENVIRONMENT == 'prd':
            # Banco de produção
            DB_PATH = os.path.join(BASE_DB_PATH, 'banco_lucy_prd')
        else:
            # Banco de desenvolvimento (padrão quando roda localmente)
            DB_PATH = os.path.join(BASE_DB_PATH, 'banco_lucy_dev')
        
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def get_environment():
        """Retorna o ambiente atual (dev ou prd)"""
        return Config.ENVIRONMENT

