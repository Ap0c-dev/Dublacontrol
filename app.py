"""
Arquivo alternativo para o Render detectar automaticamente a aplicação Flask
Se o Render não estiver usando o Procfile, ele tentará usar este arquivo
"""
from wsgi import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

