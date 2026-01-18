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
    use_credentials = False  # Por padrão, não usar credentials quando origins é '*'
    
    if allowed_origins != '*':
        # Se CORS_ORIGINS for uma string com múltiplos domínios separados por vírgula
        allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
        use_credentials = True  # Permitir credentials quando origins são específicos
    
    # Função auxiliar para adicionar headers CORS
    def add_cors_headers_to_response(response):
        """Adiciona headers CORS a uma resposta"""
        if request.path.startswith('/api/'):
            origin = request.headers.get('Origin')
            
            # Sempre adicionar headers básicos
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            
            # Determinar origem permitida
            if allowed_origins == '*':
                # Permitir qualquer origem quando configurado como '*'
                if origin:
                    response.headers.add('Access-Control-Allow-Origin', origin)
                else:
                    response.headers.add('Access-Control-Allow-Origin', '*')
            elif isinstance(allowed_origins, list):
                # Verificar se a origem está na lista permitida
                if origin and origin in allowed_origins:
                    response.headers.add('Access-Control-Allow-Origin', origin)
                    if use_credentials:
                        response.headers.add('Access-Control-Allow-Credentials', 'true')
                elif origin:
                    # Se a origem não está na lista, ainda permitir (para desenvolvimento)
                    response.headers.add('Access-Control-Allow-Origin', origin)
                else:
                    # Se não há origem, permitir qualquer
                    response.headers.add('Access-Control-Allow-Origin', '*')
            else:
                # Fallback: usar origem se disponível, senão permitir qualquer
                if origin:
                    response.headers.add('Access-Control-Allow-Origin', origin)
                else:
                    response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    if CORS_AVAILABLE:
        cors_config = {
            "origins": allowed_origins,  # Domínios permitidos (ou '*' para todos)
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
        # Só adicionar supports_credentials se não estivermos usando '*' (navegador não permite)
        if use_credentials:
            cors_config["supports_credentials"] = True
        
        CORS(app, resources={
            r"/api/*": cors_config
        })
    
    # Sempre adicionar headers CORS manualmente também (backup caso Flask-CORS falhe)
    # Isso garante que os headers sejam adicionados mesmo se Flask-CORS não funcionar
    @app.after_request
    def after_request(response):
        return add_cors_headers_to_response(response)
    
    # Flask-SQLAlchemy gerencia o engine automaticamente
    # A URL já foi processada no config.py (pgbouncer removido)
    # SQLALCHEMY_ENGINE_OPTIONS está configurado mas Flask-SQLAlchemy 3.x não suporta diretamente
    # O pooling básico funcionará, mas não otimizado. A URL limpa já resolve o problema principal.
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
    from app.models import professor, aluno, matricula, usuario, horario_professor, nota, pagamento, senha_reset, lista_espera
    
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
            
            # Migração: Adicionar coluna aluno_id se não existir (ANTES de qualquer query)
            # Esta migração deve ser executada antes de db.create_all() e antes de qualquer uso do modelo Usuario
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                # Verificar se a tabela usuarios existe
                table_names = inspector.get_table_names()
                if 'usuarios' in table_names:
                    columns = [col['name'] for col in inspector.get_columns('usuarios')]
                    
                    if 'aluno_id' not in columns:
                        print("🔄 Migração: Adicionando coluna 'aluno_id' na tabela 'usuarios'...")
                        db_uri = str(db.engine.url)
                        is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
                        
                        try:
                            if is_postgres:
                                # PostgreSQL suporta IF NOT EXISTS
                                db.session.execute(text("""
                                    ALTER TABLE usuarios 
                                    ADD COLUMN IF NOT EXISTS aluno_id INTEGER REFERENCES alunos(id)
                                """))
                            else:
                                # SQLite não suporta IF NOT EXISTS, mas já verificamos acima
                                db.session.execute(text("""
                                    ALTER TABLE usuarios 
                                    ADD COLUMN aluno_id INTEGER REFERENCES alunos(id)
                                """))
                            db.session.commit()
                            print("✅ Migração concluída: coluna 'aluno_id' adicionada")
                        except Exception as alter_error:
                            db.session.rollback()
                            error_str = str(alter_error).lower()
                            if 'already exists' in error_str or 'duplicate column' in error_str:
                                print("✅ Coluna 'aluno_id' já existe")
                            else:
                                raise
            except Exception as e:
                # Se a tabela não existe ainda, db.create_all() vai criá-la com a coluna
                db.session.rollback()
                error_str = str(e).lower()
                if 'does not exist' not in error_str and 'no such table' not in error_str:
                    print(f"⚠️  Aviso na migração: {e}")
            
            # Migração: Adicionar coluna observacao na tabela alunos se não existir
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                if 'alunos' in table_names:
                    columns = [col['name'] for col in inspector.get_columns('alunos')]
                    
                    if 'observacao' not in columns:
                        print("🔄 Migração: Adicionando coluna 'observacao' na tabela 'alunos'...")
                        db_uri = str(db.engine.url)
                        is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
                        
                        try:
                            if is_postgres:
                                # PostgreSQL suporta IF NOT EXISTS
                                db.session.execute(text("""
                                    ALTER TABLE alunos 
                                    ADD COLUMN IF NOT EXISTS observacao TEXT
                                """))
                            else:
                                # SQLite não suporta IF NOT EXISTS, mas já verificamos acima
                                db.session.execute(text("""
                                    ALTER TABLE alunos 
                                    ADD COLUMN observacao TEXT
                                """))
                            db.session.commit()
                            print("✅ Migração concluída: coluna 'observacao' adicionada na tabela 'alunos'")
                        except Exception as alter_error:
                            db.session.rollback()
                            error_str = str(alter_error).lower()
                            if 'already exists' in error_str or 'duplicate column' in error_str:
                                print("✅ Coluna 'observacao' já existe na tabela 'alunos'")
                            else:
                                raise
            except Exception as e:
                db.session.rollback()
                error_str = str(e).lower()
                if 'does not exist' not in error_str and 'no such table' not in error_str:
                    print(f"⚠️  Aviso na migração de observacao: {e}")
            
            # Migração: Criar tabela lista_espera se não existir
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                if 'lista_espera' not in table_names:
                    print("🔄 Migração: Criando tabela 'lista_espera'...")
                    db_uri = str(db.engine.url)
                    is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
                    
                    if is_postgres:
                        db.session.execute(text("""
                            CREATE TABLE IF NOT EXISTS lista_espera (
                                id SERIAL PRIMARY KEY,
                                nome VARCHAR(200) NOT NULL,
                                telefone VARCHAR(20) NOT NULL,
                                curso VARCHAR(100),
                                idade INTEGER,
                                cidade VARCHAR(100),
                                regiao VARCHAR(100),
                                estado VARCHAR(2),
                                dia_semana VARCHAR(20),
                                data_pretende_entrar DATE,
                                nome_responsavel VARCHAR(200),
                                telefone_responsavel VARCHAR(20),
                                observacao TEXT,
                                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                efetivado BOOLEAN DEFAULT FALSE NOT NULL,
                                data_efetivacao TIMESTAMP,
                                aluno_id INTEGER REFERENCES alunos(id)
                            )
                        """))
                    else:
                        db.session.execute(text("""
                            CREATE TABLE IF NOT EXISTS lista_espera (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome VARCHAR(200) NOT NULL,
                                telefone VARCHAR(20) NOT NULL,
                                curso VARCHAR(100),
                                idade INTEGER,
                                cidade VARCHAR(100),
                                regiao VARCHAR(100),
                                estado VARCHAR(2),
                                dia_semana VARCHAR(20),
                                data_pretende_entrar DATE,
                                nome_responsavel VARCHAR(200),
                                telefone_responsavel VARCHAR(20),
                                observacao TEXT,
                                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                                efetivado BOOLEAN DEFAULT 0 NOT NULL,
                                data_efetivacao DATETIME,
                                aluno_id INTEGER REFERENCES alunos(id)
                            )
                        """))
                    db.session.commit()
                    print("✅ Migração concluída: tabela 'lista_espera' criada")
            except Exception as e:
                db.session.rollback()
                error_str = str(e).lower()
                if 'already exists' not in error_str and 'duplicate' not in error_str:
                    print(f"⚠️  Aviso na migração de lista_espera: {e}")
            
            # Migração: Adicionar colunas regiao e data_pretende_entrar na tabela lista_espera se não existirem
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                table_names = inspector.get_table_names()
                if 'lista_espera' in table_names:
                    columns = [col['name'] for col in inspector.get_columns('lista_espera')]
                    
                    db_uri = str(db.engine.url)
                    is_postgres = 'postgresql' in db_uri or 'postgres' in db_uri
                    
                    if 'regiao' not in columns:
                        print("🔄 Migração: Adicionando coluna 'regiao' na tabela 'lista_espera'...")
                        try:
                            if is_postgres:
                                db.session.execute(text("""
                                    ALTER TABLE lista_espera 
                                    ADD COLUMN IF NOT EXISTS regiao VARCHAR(100)
                                """))
                            else:
                                db.session.execute(text("""
                                    ALTER TABLE lista_espera 
                                    ADD COLUMN regiao VARCHAR(100)
                                """))
                            db.session.commit()
                            print("✅ Migração concluída: coluna 'regiao' adicionada na tabela 'lista_espera'")
                        except Exception as alter_error:
                            db.session.rollback()
                            error_str = str(alter_error).lower()
                            if 'already exists' in error_str or 'duplicate column' in error_str:
                                print("✅ Coluna 'regiao' já existe na tabela 'lista_espera'")
                            else:
                                raise
                    
                    if 'data_pretende_entrar' not in columns:
                        print("🔄 Migração: Adicionando coluna 'data_pretende_entrar' na tabela 'lista_espera'...")
                        try:
                            if is_postgres:
                                db.session.execute(text("""
                                    ALTER TABLE lista_espera 
                                    ADD COLUMN IF NOT EXISTS data_pretende_entrar DATE
                                """))
                            else:
                                db.session.execute(text("""
                                    ALTER TABLE lista_espera 
                                    ADD COLUMN data_pretende_entrar DATE
                                """))
                            db.session.commit()
                            print("✅ Migração concluída: coluna 'data_pretende_entrar' adicionada na tabela 'lista_espera'")
                        except Exception as alter_error:
                            db.session.rollback()
                            error_str = str(alter_error).lower()
                            if 'already exists' in error_str or 'duplicate column' in error_str:
                                print("✅ Coluna 'data_pretende_entrar' já existe na tabela 'lista_espera'")
                            else:
                                raise
            except Exception as e:
                db.session.rollback()
                error_str = str(e).lower()
                if 'does not exist' not in error_str and 'no such table' not in error_str:
                    print(f"⚠️  Aviso na migração de lista_espera (colunas): {e}")
            
            db.create_all()
            
            # Verificar e criar usuário admin se não existir (apenas em produção)
            env = app.config.get('ENVIRONMENT', 'dev')
            if env == 'prd':
                from app.models.usuario import Usuario
                from werkzeug.security import generate_password_hash
                admin_exists = Usuario.query.filter_by(role='admin').first()
                if not admin_exists:
                    # Criar admin padrão apenas se não existir nenhum admin
                    # Gerar senha aleatória segura
                    import secrets
                    import string
                    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
                    senha_temp = ''.join(secrets.choice(caracteres) for _ in range(12))
                    admin_password = generate_password_hash(senha_temp)
                    admin = Usuario(
                        username='admin',
                        email='admin@controle-dublagem.com',
                        password_hash=admin_password,
                        role='admin',
                        ativo=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("⚠️  Usuário admin padrão criado (username: admin)")
                    print(f"⚠️  SENHA TEMPORÁRIA: {senha_temp}")
                    print("⚠️  IMPORTANTE: Anote esta senha e altere-a após o primeiro login!")
                    print("⚠️  Esta senha não será exibida novamente!")
            
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

