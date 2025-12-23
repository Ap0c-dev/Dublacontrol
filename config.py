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
        # No Render, usar diretório temporário se não houver DATABASE_URL
        if os.environ.get('RENDER'):
            # Render sem DATABASE_URL - usar diretório temporário (dados serão perdidos ao reiniciar)
            import tempfile
            temp_dir = tempfile.gettempdir()
            DB_PATH = os.path.join(temp_dir, 'controle_dublagem.db')
            # Garantir que o diretório existe
            os.makedirs(temp_dir, exist_ok=True)
            print(f"⚠️  AVISO: Usando banco SQLite temporário em {DB_PATH}")
            print("⚠️  Dados serão perdidos ao reiniciar. Configure DATABASE_URL para usar PostgreSQL.")
        else:
            # Desenvolvimento local
            BASE_DB_PATH = os.environ.get('DATABASE_PATH') or '/home/tiago'
            
            if ENVIRONMENT == 'prd':
                # Banco de produção local
                DB_PATH = os.path.join(BASE_DB_PATH, 'banco_lucy_prd')
            else:
                # Banco de desenvolvimento (padrão quando roda localmente)
                DB_PATH = os.path.join(BASE_DB_PATH, 'banco_lucy_dev')
            
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else BASE_DB_PATH, exist_ok=True)
        
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações do Cloudinary (armazenamento de comprovantes)
    # Valores padrão caso não estejam nas variáveis de ambiente
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or 'docvxvt4v'
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or ''
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or ''
    
    # Configurações do WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or ''
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or ''
    TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM') or 'whatsapp:+14155238886'
    WHATSAPP_ENABLED = os.environ.get('WHATSAPP_ENABLED', 'true').lower() == 'true'
    
    # Tamanho máximo de upload (10MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def get_environment():
        """Retorna o ambiente atual (dev ou prd)"""
        return Config.ENVIRONMENT

