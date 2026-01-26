import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Determinar ambiente (dev ou prd)
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev').lower()  # 'dev' ou 'prd'
    
    # Banco de dados
    # Verificar se está rodando no Render
    is_render = os.environ.get('RENDER') is not None
    database_url_env = os.environ.get('DATABASE_URL')
    
    # Verificar se deve usar DATABASE_URL ou SQLite local
    use_database_url = False
    if database_url_env:
        # Se não estiver no Render e a URL apontar para o Render (hostname dpg-), ignorar e usar SQLite
        if not is_render and 'dpg-' in database_url_env:
            print(f"⚠️  DATABASE_URL aponta para Render, mas rodando localmente. Usando SQLite local.")
        else:
            # Usar DATABASE_URL (Render ou outro PostgreSQL)
            use_database_url = True
    
    if use_database_url:
        # Render PostgreSQL ou outro banco via DATABASE_URL (produção)
        # Render usa postgres:// mas SQLAlchemy precisa postgresql://
        database_url = database_url_env
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # Remover parâmetro pgbouncer=true da URL (não é reconhecido pelo psycopg2)
        # O pooler funciona automaticamente na porta 6543, não precisa desse parâmetro
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote_plus
        parsed = urlparse(database_url)
        query_params = parse_qs(parsed.query)
        
        # Remover pgbouncer se existir
        if 'pgbouncer' in query_params:
            del query_params['pgbouncer']
        
        # Reconstruir URL sem pgbouncer
        new_query = urlencode(query_params, doseq=True)
        
        # Garantir que a senha está corretamente codificada na URL
        # Se a senha contém caracteres especiais, ela precisa ser URL-encoded
        # Reconstruir a URL garantindo que username e password estão corretos
        if parsed.username and parsed.password:
            # Se a senha não está codificada, codificar agora
            # Mas não codificar se já estiver codificada (evitar dupla codificação)
            try:
                from urllib.parse import unquote
                # Tentar decodificar para verificar se está codificada
                decoded_password = unquote(parsed.password)
                # Se decodificar mudou algo, significa que estava codificada
                # Se não mudou, pode precisar codificar se tiver caracteres especiais
                if decoded_password == parsed.password:
                    # Verificar se tem caracteres que precisam ser codificados
                    if any(c in parsed.password for c in ['@', ':', '/', '?', '#', '[', ']', '%']):
                        # A senha pode ter caracteres especiais, mas não está codificada
                        # Não vamos codificar aqui porque pode quebrar se já estiver correta
                        pass
            except:
                pass
        
        database_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        # Log da URL (sem senha) para debug
        if 'supabase' in database_url.lower():
            # Mascarar senha no log
            safe_url = database_url
            if '@' in safe_url:
                parts = safe_url.split('@')
                if len(parts) == 2:
                    user_pass = parts[0].split('://')[-1] if '://' in parts[0] else parts[0]
                    if ':' in user_pass:
                        user = user_pass.split(':')[0]
                        safe_url = safe_url.replace(user_pass, f"{user}:***")
                print(f"🔗 Conectando ao Supabase: {safe_url}")
            
            # Validar formato do usuário Supabase
            parsed_check = urlparse(database_url)
            if parsed_check.username:
                # No Supabase, o usuário deve ter o formato: postgres.PROJECT_REF
                # Se não começar com "postgres.", pode estar incorreto
                if not parsed_check.username.startswith('postgres.'):
                    print(f"⚠️  AVISO: Usuário Supabase pode estar incorreto: {parsed_check.username}")
                    print("   Formato esperado: postgres.PROJECT_REF (ex: postgres.tfgfklzhewesggrusupm)")
            
            # Verificar se a senha está presente
            if not parsed_check.password or parsed_check.password == '[YOUR-PASSWORD]':
                print("❌ ERRO: Senha não configurada na DATABASE_URL!")
                print("   Verifique se a senha foi substituída na variável de ambiente DATABASE_URL no Render")
                print("   A senha deve ser a senha do banco de dados do Supabase")
        
        SQLALCHEMY_DATABASE_URI = database_url
        ENVIRONMENT = 'prd'  # Se tem DATABASE_URL válida, está em produção
        
        # Configurações de connection pooling para melhor performance
        # Especialmente importante para Supabase e outros bancos remotos
        # Flask-SQLAlchemy aplica essas configurações via SQLALCHEMY_ENGINE_OPTIONS
        
        # Para PgBouncer (pooler), usar configurações mais conservadoras
        is_pgbouncer = 'pooler' in database_url and ':6543' in database_url
        
        if is_pgbouncer:
            # PgBouncer tem limitações - usar pool menor e sem prepared statements
            SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_size': 3,  # Pool menor para PgBouncer
                'max_overflow': 5,
                'pool_pre_ping': True,
                'pool_recycle': 1800,  # 30 minutos (PgBouncer recicla conexões)
                'connect_args': {
                    'connect_timeout': 10,
                    # PgBouncer não suporta prepared statements em modo transaction
                    # Usar modo session para melhor compatibilidade
                }
            }
        else:
            # Configuração padrão para conexão direta
            SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_size': 5,
                'max_overflow': 10,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'connect_args': {
                    'connect_timeout': 10,
                }
            }
        
        # Para Supabase, usar pooler se disponível (melhor performance)
        if 'supabase.co' in database_url:
            if 'pooler' in database_url and ':6543' in database_url:
                print("✅ Usando Supabase com connection pooling (PgBouncer) - Ótimo para performance!")
            elif 'pooler' not in database_url:
                print("💡 Dica: Para melhor performance no Supabase, use a URL do pooler (porta 6543)")
                print("   No Supabase: Settings → Database → Connection string → ORM's")
                print("   Use a porta 6543 (PgBouncer) ao invés de 5432")
    else:
        # SQLite local - separar dev e prd
        # No Render, usar diretório temporário se não houver DATABASE_URL
        if is_render:
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

