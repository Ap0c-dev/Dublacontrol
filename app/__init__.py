import os

# IMPORTANTE: Carregar .env ANTES de importar Config
# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    # Carregar .env da raiz do projeto
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Arquivo .env carregado: {env_path}")
    else:
        print(f"⚠️  Arquivo .env não encontrado em: {env_path}")
        print("⚠️  Usando variáveis de ambiente do sistema")
except ImportError:
    # python-dotenv não instalado, tentar carregar manualmente
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        print(f"⚠️  python-dotenv não instalado. Carregando .env manualmente...")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✓ Arquivo .env carregado manualmente")
    else:
        print("⚠️  Arquivo .env não encontrado. Usando variáveis de ambiente do sistema")

# Agora importar Config (que vai ler as variáveis de ambiente já carregadas)
from flask import Flask, request
from flask_login import LoginManager
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  Flask-CORS não instalado. API REST pode não funcionar com frontend externo.")
    print("⚠️  Instale com: pip install Flask-CORS")
from config import Config
from app.models.professor import db

def create_app():
    # Obter o diretório raiz do projeto
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Garantir que os diretórios existem
    if not os.path.exists(template_dir):
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    if not os.path.exists(static_dir):
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir,
                instance_relative_config=True)
    app.config.from_object(Config)
    
    # Configurar CORS para API (permitir frontend externo)
    # Em produção, permitir apenas domínios específicos via variável de ambiente
    allowed_origins = os.environ.get('CORS_ORIGINS', '*')
    if allowed_origins != '*':
        # Se CORS_ORIGINS for uma string com múltiplos domínios separados por vírgula
        allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
    
    if CORS_AVAILABLE:
        CORS(app, resources={
            r"/api/*": {
                "origins": allowed_origins,  # Domínios permitidos (ou '*' para todos)
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        })
    else:
        # CORS não disponível - adicionar headers manualmente para API
        @app.after_request
        def after_request(response):
            if request.path.startswith('/api/'):
                # Usar origem da requisição ou domínios permitidos
                origin = request.headers.get('Origin')
                if allowed_origins == '*' or (isinstance(allowed_origins, list) and origin and origin in allowed_origins):
                    response.headers.add('Access-Control-Allow-Origin', origin if origin else '*')
                elif allowed_origins == '*':
                    response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
                response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
                response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    # Filtro customizado para formatar valores monetários
    @app.template_filter('format_currency')
    def format_currency(value):
        """Formata um valor numérico como moeda brasileira"""
        try:
            if value is None:
                return '-'
            # Converter para float se necessário
            valor_float = float(value)
            if valor_float == 0:
                return '-'
            # Formatar com 2 casas decimais e substituir ponto por vírgula
            formatted = f"{valor_float:.2f}".replace('.', ',')
            return f"R$ {formatted}"
        except (ValueError, TypeError):
            return '-'
    
    # Filtro customizado para formatar nomes (primeira letra maiúscula, resto minúscula)
    @app.template_filter('format_name')
    def format_name(value):
        """Formata um nome com primeira letra maiúscula e resto minúscula"""
        if not value:
            return value
        try:
            # Converte para string e aplica title case
            return str(value).title()
        except (ValueError, TypeError):
            return value
    
    # Adicionar range ao contexto do template (Jinja2 não tem range por padrão)
    @app.context_processor
    def utility_processor():
        def range_func(start, stop=None, step=1):
            if stop is None:
                return list(range(start))
            return list(range(start, stop, step))
        return dict(range=range_func)
    
    # Importar modelos para garantir que as tabelas sejam criadas
    from app.models import professor, aluno, matricula, usuario, horario_professor, nota, pagamento, senha_reset
    
    # Configurar Cloudinary
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME', ''),
        api_key=app.config.get('CLOUDINARY_API_KEY', ''),
        api_secret=app.config.get('CLOUDINARY_API_SECRET', ''),
        secure=True
    )
    
    with app.app_context():
        try:
            # Verificar se o banco é SQLite e se o diretório existe
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"✓ Diretório do banco criado: {db_dir}")
            
            db.create_all()
            
            # Migração: Adicionar coluna aluno_id se não existir
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                columns = [col['name'] for col in inspector.get_columns('usuarios')]
                
                if 'aluno_id' not in columns:
                    print("🔄 Migração: Adicionando coluna 'aluno_id' na tabela 'usuarios'...")
                    db_uri = str(db.engine.url)
                    is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
                    
                    if is_postgres:
                        db.session.execute(text("""
                            ALTER TABLE usuarios 
                            ADD COLUMN IF NOT EXISTS aluno_id INTEGER REFERENCES alunos(id)
                        """))
                    else:
                        db.session.execute(text("""
                            ALTER TABLE usuarios 
                            ADD COLUMN aluno_id INTEGER REFERENCES alunos(id)
                        """))
                    db.session.commit()
                    print("✅ Migração concluída: coluna 'aluno_id' adicionada")
            except Exception as e:
                # Se a coluna já existe ou outro erro, continuar
                db.session.rollback()
                if 'already exists' not in str(e).lower() and 'duplicate column' not in str(e).lower():
                    print(f"⚠️  Aviso na migração: {e}")
            
            # Verificar e criar usuário admin se não existir (apenas em produção)
            env = app.config.get('ENVIRONMENT', 'dev')
            if env == 'prd':
                from app.models.usuario import Usuario
                from werkzeug.security import generate_password_hash
                admin_exists = Usuario.query.filter_by(role='admin').first()
                if not admin_exists:
                    # Criar admin padrão apenas se não existir nenhum admin
                    # A senha padrão deve ser alterada após o primeiro login
                    admin_password = generate_password_hash('admin123')
                    admin = Usuario(
                        username='admin',
                        email='admin@controle-dublagem.com',
                        password_hash=admin_password,
                        role='admin',
                        ativo=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("⚠️  Usuário admin padrão criado (username: admin, senha: admin123)")
                    print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            
            print(f"✓ Ambiente: {env.upper()}")
            print(f"✓ Banco de dados: {db_uri}")
            print("✓ Tabelas criadas/verificadas com sucesso")
        except Exception as e:
            print(f"✗ Erro ao criar tabelas: {e}")
            import traceback
            traceback.print_exc()
            # Não levantar exceção para não quebrar a aplicação, mas logar o erro
    
    # Registrar blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Registrar API blueprint (para frontend moderno)
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Rota de health check para o Render
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    return app

