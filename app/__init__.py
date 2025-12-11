from flask import Flask
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
    
    # Importar modelos para garantir que as tabelas sejam criadas
    from app.models import professor, aluno, matricula
    
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
            env = app.config.get('ENVIRONMENT', 'dev')
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

