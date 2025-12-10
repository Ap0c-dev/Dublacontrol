from flask import Flask
from config import Config
from app.models.professor import db
import os

def create_app():
    # Obter o diretório raiz do projeto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Importar modelos para garantir que as tabelas sejam criadas
    from app.models import professor, aluno, matricula
    
    with app.app_context():
        db.create_all()
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app

