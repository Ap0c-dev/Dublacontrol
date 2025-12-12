from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models.professor import db
import os

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
    
    # Importar modelos para garantir que as tabelas sejam criadas
    from app.models import professor, aluno, matricula, usuario, horario_professor, nota
    
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
    
    # Registrar blueprint
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Rota de health check para o Render
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    return app

