"""
API REST para integração com frontend moderno (Lovable, React, etc.)
Mantém as rotas atuais funcionando, adiciona endpoints API em paralelo
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, current_user
from app.models.professor import db, Professor
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.models.pagamento import Pagamento
from app.models.nota import Nota
from app.models.senha_reset import SenhaReset
from datetime import datetime, date
from functools import wraps
import hashlib
from calendar import monthrange
from werkzeug.utils import secure_filename
import os
import re
import unicodedata
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Armazenamento simples de tokens válidos (em produção, usar Redis ou JWT)
# Formato: {token: user_id}
valid_tokens = {}

# Rota raiz da API
@api_bp.route('/', methods=['GET'])
def api_root():
    """Rota raiz da API - retorna informações sobre a API"""
    return jsonify({
        'success': True,
        'message': 'API Voxen está funcionando!',
        'version': '1.0',
        'endpoints': {
            'test': '/api/v1/test',
            'auth': {
                'login': '/api/v1/auth/login',
                'me': '/api/v1/auth/me'
            },
            'alunos': '/api/v1/alunos',
            'professores': '/api/v1/professores',
            'pagamentos': '/api/v1/pagamentos',
            'notas': '/api/v1/notas',
            'dashboard': '/api/v1/dashboard/stats'
        }
    })

# Rota de teste simples
@api_bp.route('/test', methods=['GET'])
def api_test():
    """Rota de teste para verificar se API está funcionando"""
    return jsonify({'success': True, 'message': 'API está funcionando!'})

def api_login_required(f):
    """Decorador para autenticação API - aceita token ou sessão Flask-Login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir OPTIONS sem autenticação (para CORS preflight)
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            return response, 200
        
        # Verificar se está autenticado via Flask-Login (para testes/sessão)
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        # Verificar token na header (para API REST)
        auth_header = request.headers.get('Authorization', '')
        print(f"🔍 Authorization header recebido: {auth_header[:50] if auth_header else 'VAZIO'}...")
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            print(f"🔍 Validando token: {token[:20]}... (total tokens válidos: {len(valid_tokens)})")
            
            # Validar token
            if token in valid_tokens:
                user_id = valid_tokens[token]
                usuario = Usuario.query.get(user_id)
                if usuario:
                    print(f"✅ Token válido para usuário: {usuario.username}")
                    # Fazer login do usuário para esta requisição
                    login_user(usuario, remember=False)
                    return f(*args, **kwargs)
                else:
                    print(f"❌ Usuário não encontrado para token: {user_id}")
            else:
                print(f"❌ Token não encontrado em valid_tokens.")
                print(f"❌ Tokens disponíveis (primeiros 3): {list(valid_tokens.keys())[:3]}")
                print(f"❌ Token recebido (primeiros 20 chars): {token[:20]}")
        else:
            print(f"❌ Authorization header não começa com 'Bearer '. Header completo: {auth_header}")
        
        response = jsonify({'error': 'Não autenticado', 'message': 'Token ou sessão necessária'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 401
    return decorated_function

def api_admin_required(f):
    """Decorador para verificar se é admin na API"""
    @wraps(f)
    @api_login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Acesso negado', 'message': 'Apenas administradores'}), 403
        return f(*args, **kwargs)
    return decorated_function

def api_write_required(f):
    """Decorador para verificar se o usuário pode escrever (não é gerente/readonly)"""
    @wraps(f)
    @api_login_required
    def decorated_function(*args, **kwargs):
        if current_user.is_readonly():
            return jsonify({'error': 'Acesso negado', 'message': 'Gerentes têm apenas permissão de leitura'}), 403
        return f(*args, **kwargs)
    return decorated_function

def gerar_username_voxen(nome, role='aluno'):
    """
    Gera um username único baseado no nome + 'voxen'
    Formato: primeironome_voxen, primeironome_voxen2, etc.
    """
    # Normalizar nome: remover acentos, converter para minúsculas, remover caracteres especiais
    nome_normalizado = unicodedata.normalize('NFD', nome)
    nome_normalizado = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    nome_normalizado = re.sub(r'[^a-zA-Z0-9\s]', '', nome_normalizado)
    
    # Pegar primeiro nome
    primeiro_nome = nome_normalizado.split()[0].lower() if nome_normalizado.split() else 'user'
    
    # Se o primeiro nome for muito curto, usar mais palavras
    if len(primeiro_nome) < 3:
        palavras = nome_normalizado.split()[:2]
        primeiro_nome = '_'.join(p.lower() for p in palavras if p) or 'user'
    
    # Gerar username base: primeironome_voxen
    username_base = f"{primeiro_nome}_voxen"
    
    # Verificar se já existe e incrementar se necessário
    username = username_base
    contador = 1
    while Usuario.query.filter_by(username=username).first():
        username = f"{username_base}{contador}"
        contador += 1
        # Limite de segurança para evitar loop infinito
        if contador > 999:
            # Se chegar a 999, usar timestamp
            username = f"{username_base}_{int(datetime.now().timestamp())}"
            break
    
    return username

# ==================== AUTENTICAÇÃO ====================

@api_bp.route('/auth/login', methods=['POST', 'OPTIONS'])
def api_login():
    """Login via API - retorna token simples (pode melhorar com JWT depois)"""
    # Tratar OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    try:
        # Aceitar JSON mesmo se Content-Type não estiver correto
        data = request.get_json(force=True, silent=True)
        
        # Se não conseguiu pegar JSON, tentar do form
        if not data:
            data = request.form.to_dict() or {}
        
        username = data.get('username', '').strip() if data else ''
        password = data.get('password', '').strip() if data else ''
        
        if not username or not password:
            response = jsonify({'error': 'Username e password são obrigatórios', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        # Verificar se usuário existe
        if not usuario:
            print(f"❌ Tentativa de login com usuário inexistente: {username}")
            response = jsonify({'error': 'Credenciais inválidas', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 401
        
        # Verificar se usuário está ativo
        if not usuario.ativo:
            print(f"❌ Tentativa de login com usuário inativo: {username}")
            response = jsonify({'error': 'Usuário inativo. Entre em contato com o administrador.', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 403
        
        # Verificar senha
        if not usuario.check_password(password):
            print(f"❌ Tentativa de login com senha incorreta para usuário: {username}")
            response = jsonify({'error': 'Credenciais inválidas', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 401
        
        # Login via Flask-Login (para manter compatibilidade)
        login_user(usuario, remember=True)
        
        # Gerar token simples (pode melhorar com JWT depois)
        token = hashlib.sha256(f"{usuario.id}{usuario.username}{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Armazenar token válido
        valid_tokens[token] = usuario.id
        print(f"✅ Token gerado e armazenado: {token[:20]}... para usuário {usuario.username} (ID: {usuario.id})")
        print(f"📊 Total de tokens válidos: {len(valid_tokens)}")
        
        # Buscar nome do professor se for professor, ou do aluno se for aluno
        nome = usuario.username
        if usuario.is_professor() and usuario.professor:
            nome = usuario.professor.nome
        elif usuario.is_aluno() and usuario.aluno:
            nome = usuario.aluno.nome
        
        response = jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': usuario.id,
                'username': usuario.username,
                'nome': nome,  # Nome do usuário, professor ou aluno associado
                'role': usuario.role,
                'is_admin': usuario.is_admin(),
                'is_professor': usuario.is_professor(),
                'is_aluno': usuario.is_aluno(),
                'is_gerente': usuario.is_gerente(),
                'is_readonly': usuario.is_readonly(),
                'professor_id': usuario.professor_id,
                'aluno_id': usuario.aluno_id
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Erro no login API: {error_trace}")
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/auth/me', methods=['GET'])
@api_login_required
def api_me():
    """Retorna informações do usuário atual"""
    # Buscar nome do professor se for professor, ou do aluno se for aluno
    nome = current_user.username
    if current_user.is_professor() and current_user.professor:
        nome = current_user.professor.nome
    elif current_user.is_aluno() and current_user.aluno:
        nome = current_user.aluno.nome
    
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'nome': nome,
        'role': current_user.role,
        'is_admin': current_user.is_admin(),
        'is_professor': current_user.is_professor(),
        'is_aluno': current_user.is_aluno(),
        'is_gerente': current_user.is_gerente(),
        'is_readonly': current_user.is_readonly(),
        'professor_id': current_user.professor_id if hasattr(current_user, 'professor_id') else None,
        'aluno_id': current_user.aluno_id if hasattr(current_user, 'aluno_id') else None
    })

# ==================== RECUPERAÇÃO DE SENHA ====================

@api_bp.route('/auth/reset-password/generate-code', methods=['POST'])
@api_admin_required
def api_gerar_codigo_recuperacao():
    """Gera um código de recuperação de senha para um usuário (apenas admin)"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        username = data.get('username', '').strip()
        
        if not username:
            response = jsonify({'error': 'Username é obrigatório', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            response = jsonify({'error': 'Usuário não encontrado', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # Criar código de recuperação
        reset = SenhaReset.criar_codigo(usuario.id, criado_por_admin=current_user.id)
        
        response = jsonify({
            'success': True,
            'codigo': reset.codigo,
            'usuario': usuario.username,
            'valido_ate': reset.data_expiracao.isoformat(),
            'message': f'Código gerado com sucesso. Compartilhe este código com o usuário: {reset.codigo}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        import traceback
        print(f"Erro ao gerar código de recuperação: {traceback.format_exc()}")
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/auth/reset-password/use-code', methods=['POST', 'OPTIONS'])
def api_usar_codigo_recuperacao():
    """Usa um código de recuperação para resetar a senha"""
    # Tratar OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    try:
        data = request.get_json(force=True, silent=True) or {}
        codigo = data.get('codigo', '').strip().upper()
        nova_senha = data.get('nova_senha', '').strip()
        
        if not codigo or not nova_senha:
            response = jsonify({'error': 'Código e nova senha são obrigatórios', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        if len(nova_senha) < 6:
            response = jsonify({'error': 'A senha deve ter pelo menos 6 caracteres', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Buscar código de recuperação
        reset = SenhaReset.query.filter_by(codigo=codigo).first()
        
        if not reset:
            response = jsonify({'error': 'Código inválido', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        if not reset.is_valido():
            response = jsonify({'error': 'Código expirado ou já utilizado', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Resetar senha do usuário
        reset.usuario.set_password(nova_senha)
        reset.usar()  # Marcar código como usado
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Senha alterada com sucesso! Você já pode fazer login.'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao usar código de recuperação: {traceback.format_exc()}")
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/auth/reset-password/admin', methods=['POST'])
@api_admin_required
def api_reset_senha_admin():
    """Admin reseta a senha de um usuário diretamente"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        username = data.get('username', '').strip()
        nova_senha = data.get('nova_senha', '').strip()
        
        if not username or not nova_senha:
            response = jsonify({'error': 'Username e nova senha são obrigatórios', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        if len(nova_senha) < 6:
            response = jsonify({'error': 'A senha deve ter pelo menos 6 caracteres', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            response = jsonify({'error': 'Usuário não encontrado', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 404
        
        # Resetar senha
        usuario.set_password(nova_senha)
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': f'Senha do usuário "{username}" resetada com sucesso!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao resetar senha via admin: {traceback.format_exc()}")
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/auth/reset-password/change', methods=['POST'])
@api_login_required
def api_alterar_senha():
    """Usuário autenticado altera sua própria senha"""
    try:
        data = request.get_json(force=True, silent=True) or {}
        senha_atual = data.get('senha_atual', '').strip()
        nova_senha = data.get('nova_senha', '').strip()
        
        if not senha_atual or not nova_senha:
            response = jsonify({'error': 'Senha atual e nova senha são obrigatórias', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        if len(nova_senha) < 6:
            response = jsonify({'error': 'A nova senha deve ter pelo menos 6 caracteres', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Verificar senha atual
        if not current_user.check_password(senha_atual):
            response = jsonify({'error': 'Senha atual incorreta', 'success': False})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 401
        
        # Alterar senha
        current_user.set_password(nova_senha)
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Senha alterada com sucesso!'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao alterar senha: {traceback.format_exc()}")
        response = jsonify({'error': str(e), 'success': False})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# ==================== ALUNOS ====================

@api_bp.route('/alunos', methods=['GET'])
@api_login_required
def api_listar_alunos():
    """Lista todos os alunos (com filtros opcionais e filtragem por role)"""
    try:
        # Filtros opcionais
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        aprovado = request.args.get('aprovado')
        search = request.args.get('search', '').strip()
        professor_id = request.args.get('professor_id')
        
        query = Aluno.query
        
        # FILTRAGEM AUTOMÁTICA POR ROLE
        # Professor: vê apenas seus alunos
        if current_user.is_professor() and current_user.professor_id:
            query = query.join(Matricula).filter(Matricula.professor_id == current_user.professor_id).distinct()
        # Aluno: vê apenas seus próprios dados
        elif current_user.is_aluno() and current_user.aluno_id:
            query = query.filter_by(id=current_user.aluno_id)
        # Admin e Gerente: vêem todos (sem filtro adicional)
        
        if ativo:
            query = query.filter_by(ativo=True)
        
        if aprovado is not None:
            query = query.filter_by(aprovado=aprovado.lower() == 'true')
        
        # Filtrar por professor (através das matrículas) - apenas se não for professor logado
        if professor_id and not current_user.is_professor():
            try:
                professor_id_int = int(professor_id)
                query = query.join(Matricula).filter(Matricula.professor_id == professor_id_int).distinct()
            except ValueError:
                pass  # Ignorar se professor_id não for um número válido
        
        if search:
            query = query.filter(
                db.or_(
                    Aluno.nome.ilike(f'%{search}%'),
                    Aluno.telefone.ilike(f'%{search}%')
                )
            )
        
        alunos = query.order_by(Aluno.nome).all()
        
        resultado = []
        for aluno in alunos:
            # Determinar status para compatibilidade com frontend
            if not aluno.ativo:
                status = 'inativo'
            elif not aluno.aprovado:
                status = 'pendente'
            else:
                status = 'ativo'
            
            resultado.append({
                'id': aluno.id,
                'nome': aluno.nome,
                'email': '',  # Campo não existe no modelo, mas frontend espera
                'telefone': aluno.telefone,
                'telefone_responsavel': aluno.telefone_responsavel,
                'nome_responsavel': aluno.nome_responsavel,
                'cidade': aluno.cidade,
                'estado': aluno.estado,
                'data_nascimento': aluno.data_nascimento.isoformat() if aluno.data_nascimento else None,
                'data_vencimento': aluno.data_vencimento.isoformat() if aluno.data_vencimento else None,
                'forma_pagamento': aluno.forma_pagamento,
                'total_mensalidades': aluno.get_total_mensalidades(),
                'ativo': aluno.ativo,
                'aprovado': aluno.aprovado,
                'experimental': aluno.experimental,
                'status': status,  # Campo esperado pelo frontend
                'status_vencimento': aluno.get_status_vencimento(),
                'created_at': aluno.data_cadastro.isoformat() if aluno.data_cadastro else None,  # Campo esperado pelo frontend
                'modalidades': {
                    'dublagem_online': aluno.dublagem_online,
                    'dublagem_presencial': aluno.dublagem_presencial,
                    'teatro_online': aluno.teatro_online,
                    'teatro_presencial': aluno.teatro_presencial,
                    'locucao': aluno.locucao,
                    'teatro_tv_cinema': aluno.teatro_tv_cinema,
                    'musical': aluno.musical
                }
            })
        
        return jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alunos/<int:aluno_id>', methods=['GET'])
@api_login_required
def api_get_aluno(aluno_id):
    """Busca um aluno específico (com verificação de permissão por role)"""
    try:
        aluno = Aluno.query.get_or_404(aluno_id)
        
        # Verificar permissão de acesso
        # Professor: só pode ver seus alunos
        if current_user.is_professor() and current_user.professor_id:
            matriculas = Matricula.query.filter_by(aluno_id=aluno_id, professor_id=current_user.professor_id).first()
            if not matriculas:
                return jsonify({'error': 'Acesso negado', 'message': 'Você não tem permissão para ver este aluno'}), 403
        # Aluno: só pode ver seus próprios dados
        elif current_user.is_aluno() and current_user.aluno_id:
            if aluno_id != current_user.aluno_id:
                return jsonify({'error': 'Acesso negado', 'message': 'Você só pode ver seus próprios dados'}), 403
        # Admin e Gerente: podem ver todos
        
        # Buscar matrículas
        matriculas = Matricula.query.filter_by(aluno_id=aluno_id).all()
        matriculas_data = []
        for mat in matriculas:
            matriculas_data.append({
                'id': mat.id,
                'professor_id': mat.professor_id,
                'professor_nome': mat.professor.nome if mat.professor else None,
                'tipo_curso': mat.tipo_curso,
                'valor_mensalidade': float(mat.valor_mensalidade) if mat.valor_mensalidade else 0,
                'dia_semana': mat.dia_semana,
                'horario_aula': mat.horario_aula,
                'data_inicio': mat.data_inicio.isoformat() if mat.data_inicio else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'id': aluno.id,
                'nome': aluno.nome,
                'telefone': aluno.telefone,
                'telefone_responsavel': aluno.telefone_responsavel,
                'nome_responsavel': aluno.nome_responsavel,
                'cidade': aluno.cidade,
                'estado': aluno.estado,
                'data_nascimento': aluno.data_nascimento.isoformat() if aluno.data_nascimento else None,
                'idade': aluno.idade,
                'data_vencimento': aluno.data_vencimento.isoformat() if aluno.data_vencimento else None,
                'forma_pagamento': aluno.forma_pagamento,
                'total_mensalidades': aluno.get_total_mensalidades(),
                'ativo': aluno.ativo,
                'aprovado': aluno.aprovado,
                'experimental': aluno.experimental,
                'status_vencimento': aluno.get_status_vencimento(),
                'modalidades': {
                    'dublagem_online': aluno.dublagem_online,
                    'dublagem_presencial': aluno.dublagem_presencial,
                    'teatro_online': aluno.teatro_online,
                    'teatro_presencial': aluno.teatro_presencial,
                    'locucao': aluno.locucao,
                    'teatro_tv_cinema': aluno.teatro_tv_cinema,
                    'musical': aluno.musical
                },
                'matriculas': matriculas_data
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PROFESSORES ====================

@api_bp.route('/professores', methods=['GET'])
@api_login_required
def api_listar_professores():
    """Lista todos os professores"""
    try:
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        tipo_curso = request.args.get('tipo_curso', '').strip()
        
        query = Professor.query
        if ativo:
            query = query.filter_by(ativo=True)
        
        # Filtrar por tipo de curso se especificado
        if tipo_curso:
            from sqlalchemy import or_
            if tipo_curso == 'dublagem_online':
                query = query.filter(Professor.dublagem_online == True)
            elif tipo_curso == 'dublagem_presencial':
                query = query.filter(Professor.dublagem_presencial == True)
            # ... adicionar outros tipos conforme necessário
        
        professores = query.order_by(Professor.nome).all()
        
        resultado = []
        for prof in professores:
            # Determinar especialidade baseada nas modalidades
            # Converter valores booleanos/numéricos para garantir comparação correta
            # SQLite armazena booleanos como INTEGER (0/1), então precisamos converter explicitamente
            dublagem_online = bool(prof.dublagem_online) if prof.dublagem_online is not None else False
            dublagem_presencial = bool(prof.dublagem_presencial) if prof.dublagem_presencial is not None else False
            teatro_online = bool(prof.teatro_online) if prof.teatro_online is not None else False
            teatro_presencial = bool(prof.teatro_presencial) if prof.teatro_presencial is not None else False
            teatro_tv_cinema = bool(prof.teatro_tv_cinema) if prof.teatro_tv_cinema is not None else False
            locucao = bool(prof.locucao) if prof.locucao is not None else False
            musical = bool(prof.musical) if prof.musical is not None else False
            curso_apresentador = bool(prof.curso_apresentador) if prof.curso_apresentador is not None else False
            
            especialidades = []
            if dublagem_online or dublagem_presencial:
                especialidades.append('Dublagem')
            if teatro_online or teatro_presencial or teatro_tv_cinema:
                especialidades.append('Teatro')
            if locucao:
                especialidades.append('Locução')
            if musical:
                especialidades.append('Musical')
            if curso_apresentador:
                especialidades.append('Apresentador')
            
            especialidade_str = ', '.join(especialidades) if especialidades else 'Geral'
            
            resultado.append({
                'id': prof.id,
                'nome': prof.nome,
                'email': '',  # Campo não existe no modelo, mas frontend espera
                'telefone': prof.telefone,
                'especialidade': especialidade_str,  # Campo esperado pelo frontend
                'status': 'ativo' if prof.ativo else 'inativo',  # Campo esperado pelo frontend
                'dublagem_online': bool(prof.dublagem_online),
                'dublagem_presencial': bool(prof.dublagem_presencial),
                'teatro_online': bool(prof.teatro_online),
                'teatro_presencial': bool(prof.teatro_presencial),
                'locucao': bool(prof.locucao),
                'musical': bool(prof.musical),
                'teatro_tv_cinema': bool(prof.teatro_tv_cinema),
                'curso_apresentador': bool(prof.curso_apresentador),
                'ativo': bool(prof.ativo) if prof.ativo is not None else True
            })
        
        return jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/professores/por-modalidade', methods=['GET', 'OPTIONS'])
@api_login_required
def api_professores_por_modalidade():
    """Lista professores filtrados por modalidade"""
    # Tratar OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    print(f"🔍 GET /professores/por-modalidade - Usuário autenticado: {current_user.is_authenticated}")
    print(f"🔍 Headers Authorization: {request.headers.get('Authorization', 'NÃO ENCONTRADO')}")
    
    try:
        modalidade = request.args.get('modalidade', '').strip()
        if not modalidade:
            response = jsonify({'error': 'Parâmetro modalidade é obrigatório'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Mapear modalidade para campo do modelo
        modalidade_map = {
            'dublagem_online': 'dublagem_online',
            'dublagem_presencial': 'dublagem_presencial',
            'teatro_online': 'teatro_online',
            'teatro_presencial': 'teatro_presencial',
            'locucao': 'locucao',
            'teatro_tv_cinema': 'teatro_tv_cinema',
            'musical': 'musical',
            'curso_apresentador': 'curso_apresentador'
        }
        
        campo_modalidade = modalidade_map.get(modalidade)
        if not campo_modalidade:
            response = jsonify({'error': 'Modalidade inválida'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Buscar professores com essa modalidade
        query = Professor.query.filter_by(ativo=True)
        query = query.filter(getattr(Professor, campo_modalidade) == True)
        
        professores = query.order_by(Professor.nome).all()
        
        resultado = []
        for prof in professores:
            resultado.append({
                'id': prof.id,
                'nome': prof.nome,
                'telefone': prof.telefone
            })
        
        response = jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/professores/<int:professor_id>/horarios', methods=['GET', 'OPTIONS'])
@api_login_required
def api_horarios_professor(professor_id):
    """Lista horários de um professor, opcionalmente filtrados por modalidade"""
    # Tratar OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    
    print(f"🔍 GET /professores/{professor_id}/horarios - Usuário autenticado: {current_user.is_authenticated}")
    
    try:
        from app.models.horario_professor import HorarioProfessor
        
        modalidade = request.args.get('modalidade', '').strip()
        print(f"🔍 Modalidade filtro: '{modalidade}'")
        
        query = HorarioProfessor.query.filter_by(professor_id=professor_id)
        if modalidade:
            query = query.filter_by(modalidade=modalidade)
        
        horarios = query.order_by(HorarioProfessor.dia_semana, HorarioProfessor.horario_aula).all()
        print(f"🔍 Horários encontrados: {len(horarios)}")
        
        resultado = []
        for horario in horarios:
            resultado.append({
                'id': horario.id,
                'dia_semana': horario.dia_semana,
                'horario_aula': horario.horario_aula,
                'modalidade': horario.modalidade,
                'idade_minima': horario.idade_minima,
                'idade_maxima': horario.idade_maxima
            })
        
        print(f"✅ Retornando {len(resultado)} horários")
        response = jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        import traceback
        print(f"❌ Erro ao buscar horários: {str(e)}")
        print(traceback.format_exc())
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/professores/<int:professor_id>', methods=['GET'])
@api_login_required
def api_get_professor(professor_id):
    """Busca um professor específico"""
    try:
        from app.models.horario_professor import HorarioProfessor
        
        professor = Professor.query.get_or_404(professor_id)
        
        # Buscar horários do professor
        horarios = HorarioProfessor.query.filter_by(professor_id=professor.id).all()
        horarios_data = [h.to_dict() for h in horarios]
        
        # Determinar especialidade baseada nas modalidades
        # Converter valores booleanos/numéricos para garantir comparação correta
        # SQLite armazena booleanos como INTEGER (0/1), então precisamos converter explicitamente
        dublagem_online = bool(professor.dublagem_online) if professor.dublagem_online is not None else False
        dublagem_presencial = bool(professor.dublagem_presencial) if professor.dublagem_presencial is not None else False
        teatro_online = bool(professor.teatro_online) if professor.teatro_online is not None else False
        teatro_presencial = bool(professor.teatro_presencial) if professor.teatro_presencial is not None else False
        teatro_tv_cinema = bool(professor.teatro_tv_cinema) if professor.teatro_tv_cinema is not None else False
        locucao = bool(professor.locucao) if professor.locucao is not None else False
        musical = bool(professor.musical) if professor.musical is not None else False
        curso_apresentador = bool(professor.curso_apresentador) if professor.curso_apresentador is not None else False
        
        especialidades = []
        if dublagem_online or dublagem_presencial:
            especialidades.append('Dublagem')
        if teatro_online or teatro_presencial or teatro_tv_cinema:
            especialidades.append('Teatro')
        if locucao:
            especialidades.append('Locução')
        if musical:
            especialidades.append('Musical')
        if curso_apresentador:
            especialidades.append('Apresentador')
        
        especialidade_str = ', '.join(especialidades) if especialidades else 'Geral'
        
        return jsonify({
            'success': True,
            'data': {
                'id': professor.id,
                'nome': professor.nome,
                'email': '',
                'telefone': professor.telefone,
                'especialidade': especialidade_str,
                'status': 'ativo' if professor.ativo else 'inativo',
                'dublagem_online': professor.dublagem_online,
                'dublagem_presencial': professor.dublagem_presencial,
                'teatro_online': professor.teatro_online,
                'teatro_presencial': professor.teatro_presencial,
                'locucao': professor.locucao,
                'musical': professor.musical,
                'teatro_tv_cinema': professor.teatro_tv_cinema,
                'curso_apresentador': professor.curso_apresentador,
                'ativo': professor.ativo,
                'dia_semana': professor.dia_semana,
                'horario_aula': professor.horario_aula,
                'horarios': horarios_data
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PAGAMENTOS ====================

@api_bp.route('/pagamentos', methods=['GET'])
@api_login_required
def api_listar_pagamentos():
    """Lista alunos com status de pagamento calculado (como no sistema antigo)"""
    try:
        status_filtro = request.args.get('status')
        aluno_id_filtro = request.args.get('aluno_id', type=int)
        professor_id_filtro = request.args.get('professor_id', type=int)
        mes_filtro = request.args.get('mes', type=int)
        ano_filtro = request.args.get('ano', type=int)
        
        print(f"🔍 Filtros recebidos: aluno_id={aluno_id_filtro}, professor_id={professor_id_filtro}, status={status_filtro}, mes={mes_filtro}, ano={ano_filtro}")
        print(f"📊 Status filtro: '{status_filtro}' (tipo: {type(status_filtro)})")
        
        hoje = date.today()
        # Se não especificar mês/ano, retornar TODOS os pagamentos
        retornar_todos = not mes_filtro and not ano_filtro
        
        if retornar_todos:
            # Buscar TODOS os pagamentos registrados
            query_pagamentos = Pagamento.query
            
            # FILTRAGEM AUTOMÁTICA POR ROLE
            # Professor: vê apenas pagamentos dos seus alunos
            if current_user.is_professor() and current_user.professor_id:
                query_pagamentos = query_pagamentos.join(Aluno).join(Matricula).filter(
                    Matricula.professor_id == current_user.professor_id
                ).distinct()
            # Aluno: vê apenas seus próprios pagamentos
            elif current_user.is_aluno() and current_user.aluno_id:
                query_pagamentos = query_pagamentos.filter_by(aluno_id=current_user.aluno_id)
            # Admin e Gerente: vêem todos
            
            if aluno_id_filtro:
                query_pagamentos = query_pagamentos.filter_by(aluno_id=aluno_id_filtro)
            
            # Filtrar por professor através de matrículas - apenas se não for professor logado
            if professor_id_filtro and not current_user.is_professor():
                query_pagamentos = query_pagamentos.join(Aluno).join(Matricula).filter(
                    Matricula.professor_id == professor_id_filtro
                ).distinct()
            
            # Aplicar filtro de status
            # Para "atrasado", precisamos buscar rejeitados + pendentes (verificaremos depois quais pendentes estão atrasados)
            if status_filtro:
                if status_filtro == 'pago':
                    query_pagamentos = query_pagamentos.filter_by(status='aprovado')
                elif status_filtro == 'pendente':
                    query_pagamentos = query_pagamentos.filter_by(status='pendente')
                elif status_filtro == 'atrasado':
                    # Atrasados: rejeitados + pendentes (verificaremos depois quais pendentes estão atrasados)
                    query_pagamentos = query_pagamentos.filter(
                        or_(
                            Pagamento.status == 'rejeitado',
                            Pagamento.status == 'pendente'
                        )
                    )
            
            pagamentos = query_pagamentos.order_by(Pagamento.ano_referencia.desc(), Pagamento.mes_referencia.desc(), Pagamento.data_cadastro.desc()).all()
            
            print(f"📋 Total de pagamentos encontrados na query: {len(pagamentos)}")
            if pagamentos:
                print(f"📋 Status dos primeiros pagamentos: {[p.status for p in pagamentos[:5]]}")
            
            resultado = []
            meses = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            
            for pagamento in pagamentos:
                aluno = pagamento.aluno
                if not aluno or not aluno.ativo:
                    continue
                
                # Calcular data de vencimento baseada no aluno e mês/ano de referência
                data_vencimento_ref = None
                if aluno.data_vencimento:
                    dia_vencimento = aluno.data_vencimento.day
                    try:
                        data_vencimento_ref = date(pagamento.ano_referencia, pagamento.mes_referencia, dia_vencimento)
                    except ValueError:
                        ultimo_dia = monthrange(pagamento.ano_referencia, pagamento.mes_referencia)[1]
                        data_vencimento_ref = date(pagamento.ano_referencia, pagamento.mes_referencia, min(dia_vencimento, ultimo_dia))
                
                # Converter status do banco para frontend
                if pagamento.status == 'aprovado':
                    status_pagamento = 'pago'
                elif pagamento.status == 'pendente':
                    # Verificar se está atrasado (vencimento passou)
                    if data_vencimento_ref and data_vencimento_ref < hoje:
                        status_pagamento = 'atrasado'
                    else:
                        status_pagamento = 'pendente'
                elif pagamento.status == 'rejeitado':
                    status_pagamento = 'atrasado'
                else:
                    status_pagamento = 'pendente'
                
                # Aplicar filtro de status se especificado
                # IMPORTANTE: Filtrar DEPOIS de calcular o status real (pendente pode virar atrasado)
                if status_filtro:
                    if status_filtro == 'pago':
                        # Apenas pagos (aprovados)
                        if status_pagamento != 'pago':
                            continue
                    elif status_filtro == 'pendente':
                        # Apenas pendentes (NÃO incluir os que viraram atrasados)
                        if status_pagamento != 'pendente':
                            continue
                    elif status_filtro == 'atrasado':
                        # Apenas atrasados (rejeitados + pendentes que estão atrasados)
                        if status_pagamento != 'atrasado':
                            continue
                
                valor_pago = float(pagamento.valor_pago) if pagamento.valor_pago else 0
                mes_nome = meses.get(pagamento.mes_referencia, f'Mês {pagamento.mes_referencia}')
                
                resultado.append({
                    'id': pagamento.id,
                    'aluno_id': aluno.id,
                    'aluno_nome': aluno.nome,
                    'mes_referencia': pagamento.mes_referencia,
                    'ano_referencia': pagamento.ano_referencia,
                    'mes_nome': mes_nome,
                    'valor': valor_pago if valor_pago > 0 else aluno.get_total_mensalidades(),
                    'valor_pago': valor_pago,
                    'data_vencimento': data_vencimento_ref.isoformat() if data_vencimento_ref else None,
                    'data_pagamento': pagamento.data_pagamento.isoformat() if pagamento.data_pagamento else None,
                    'status': status_pagamento,
                    'status_label': 'Pago' if status_pagamento == 'pago' else 'Pendente' if status_pagamento == 'pendente' else 'Atrasado',
                    'url_comprovante': pagamento.url_comprovante,
                    'observacoes': pagamento.observacoes,
                    'data_cadastro': pagamento.data_cadastro.isoformat() if pagamento.data_cadastro else None
                })
            
            # Adicionar alunos atrasados sem pagamento registrado (apenas se o filtro for "atrasado")
            # Quando não há filtro, não adicionar alunos sem pagamento, apenas mostrar os pagamentos registrados
            if status_filtro == 'atrasado':
                query_alunos = Aluno.query.filter_by(ativo=True)
                
                # FILTRAGEM AUTOMÁTICA POR ROLE
                if current_user.is_professor() and current_user.professor_id:
                    query_alunos = query_alunos.join(Matricula).filter(Matricula.professor_id == current_user.professor_id).distinct()
                elif current_user.is_aluno() and current_user.aluno_id:
                    query_alunos = query_alunos.filter_by(id=current_user.aluno_id)
                
                if aluno_id_filtro:
                    query_alunos = query_alunos.filter_by(id=aluno_id_filtro)
                
                if professor_id_filtro and not current_user.is_professor():
                    query_alunos = query_alunos.join(Matricula).filter(
                        Matricula.professor_id == professor_id_filtro
                    ).distinct()
                
                alunos = query_alunos.order_by(Aluno.nome).all()
                for aluno in alunos:
                    if aluno.data_vencimento:
                        # Calcular data de vencimento para o mês atual
                        mes_atual = hoje.month
                        ano_atual = hoje.year
                        dia_vencimento = aluno.data_vencimento.day
                        try:
                            data_vencimento_ref = date(ano_atual, mes_atual, dia_vencimento)
                        except ValueError:
                            ultimo_dia = monthrange(ano_atual, mes_atual)[1]
                            data_vencimento_ref = date(ano_atual, mes_atual, min(dia_vencimento, ultimo_dia))
                        
                        if data_vencimento_ref < hoje:
                            # Verificar se já não está na lista de pagamentos
                            ja_existe = any(p['aluno_id'] == aluno.id for p in resultado)
                            if not ja_existe:
                                # Verificar se há pagamento pendente ou rejeitado para este mês
                                pagamento_existente = Pagamento.query.filter_by(
                                    aluno_id=aluno.id,
                                    mes_referencia=mes_atual,
                                    ano_referencia=ano_atual
                                ).first()
                                
                                # Só adicionar se não houver pagamento ou se o pagamento não estiver aprovado
                                if not pagamento_existente or pagamento_existente.status != 'aprovado':
                                    mes_nome = meses.get(mes_atual, f'Mês {mes_atual}')
                                    resultado.append({
                                        'id': f'aluno_{aluno.id}_{mes_atual}_{ano_atual}',
                                        'aluno_id': aluno.id,
                                        'aluno_nome': aluno.nome,
                                        'mes_referencia': mes_atual,
                                        'ano_referencia': ano_atual,
                                        'mes_nome': mes_nome,
                                        'valor': aluno.get_total_mensalidades(),
                                        'valor_pago': 0,
                                        'data_vencimento': data_vencimento_ref.isoformat() if data_vencimento_ref else None,
                                        'data_pagamento': None,
                                        'status': 'atrasado',
                                        'status_label': 'Atrasado',
                                        'url_comprovante': None,
                                        'observacoes': None,
                                        'data_cadastro': None
                                    })
                                    mes_nome = meses.get(mes_atual, f'Mês {mes_atual}')
                                    resultado.append({
                                        'id': f'aluno_{aluno.id}_{mes_atual}_{ano_atual}',
                                        'aluno_id': aluno.id,
                                        'aluno_nome': aluno.nome,
                                        'mes_referencia': mes_atual,
                                        'ano_referencia': ano_atual,
                                        'mes_nome': mes_nome,
                                        'valor': aluno.get_total_mensalidades(),
                                        'valor_pago': 0,
                                        'data_vencimento': aluno.data_vencimento.isoformat() if aluno.data_vencimento else None,
                                        'data_pagamento': None,
                                        'status': 'atrasado',
                                        'status_label': 'Atrasado',
                                        'url_comprovante': None,
                                        'observacoes': None,
                                        'data_cadastro': None
                                    })
        else:
            # Comportamento original: filtrar por mês/ano específico
            mes_referencia = mes_filtro if mes_filtro else hoje.month
            ano_referencia = ano_filtro if ano_filtro else hoje.year
            
            # Buscar alunos ativos (com filtragem por role)
            query_alunos = Aluno.query.filter_by(ativo=True)
            
            # FILTRAGEM AUTOMÁTICA POR ROLE
            if current_user.is_professor() and current_user.professor_id:
                query_alunos = query_alunos.join(Matricula).filter(Matricula.professor_id == current_user.professor_id).distinct()
            elif current_user.is_aluno() and current_user.aluno_id:
                query_alunos = query_alunos.filter_by(id=current_user.aluno_id)
            
            if aluno_id_filtro:
                query_alunos = query_alunos.filter_by(id=aluno_id_filtro)
            
            if professor_id_filtro and not current_user.is_professor():
                query_alunos = query_alunos.join(Matricula).filter(
                    Matricula.professor_id == professor_id_filtro
                ).distinct()
            
            alunos = query_alunos.order_by(Aluno.nome).all()
            
            resultado = []
            for aluno in alunos:
                data_vencimento_ref = None
                if aluno.data_vencimento:
                    dia_vencimento = aluno.data_vencimento.day
                    try:
                        data_vencimento_ref = date(ano_referencia, mes_referencia, dia_vencimento)
                    except ValueError:
                        ultimo_dia = monthrange(ano_referencia, mes_referencia)[1]
                        data_vencimento_ref = date(ano_referencia, mes_referencia, min(dia_vencimento, ultimo_dia))
                
                pagamento = Pagamento.query.filter_by(
                    aluno_id=aluno.id,
                    mes_referencia=mes_referencia,
                    ano_referencia=ano_referencia
                ).first()
                
                status_pagamento = None
                valor_pago = 0
                data_pagamento = None
                url_comprovante = None
                pagamento_id = None
                
                if pagamento:
                    pagamento_id = pagamento.id
                    valor_pago = float(pagamento.valor_pago) if pagamento.valor_pago else 0
                    data_pagamento = pagamento.data_pagamento.isoformat() if pagamento.data_pagamento else None
                    url_comprovante = pagamento.url_comprovante
                    
                    if pagamento.status == 'aprovado':
                        status_pagamento = 'pago'
                    elif pagamento.status == 'pendente':
                        status_pagamento = 'pendente'
                    elif pagamento.status == 'rejeitado':
                        status_pagamento = 'atrasado'
                else:
                    if data_vencimento_ref and data_vencimento_ref < hoje:
                        status_pagamento = 'atrasado'
                    else:
                        continue
                
                if status_filtro:
                    if status_filtro == 'pago' and status_pagamento != 'pago':
                        continue
                    elif status_filtro == 'pendente' and status_pagamento != 'pendente':
                        continue
                    elif status_filtro == 'atrasado' and status_pagamento != 'atrasado':
                        continue
                
                meses = {
                    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                }
                mes_nome = meses.get(mes_referencia, f'Mês {mes_referencia}')
                
                resultado.append({
                    'id': pagamento_id if pagamento_id else f'aluno_{aluno.id}_{mes_referencia}_{ano_referencia}',
                    'aluno_id': aluno.id,
                    'aluno_nome': aluno.nome,
                    'mes_referencia': mes_referencia,
                    'ano_referencia': ano_referencia,
                    'mes_nome': mes_nome,
                    'valor': valor_pago if valor_pago > 0 else aluno.get_total_mensalidades(),
                    'valor_pago': valor_pago,
                    'data_vencimento': data_vencimento_ref.isoformat() if data_vencimento_ref else None,
                    'data_pagamento': data_pagamento,
                    'status': status_pagamento or 'atrasado',
                    'status_label': 'Pago' if status_pagamento == 'pago' else 'Pendente' if status_pagamento == 'pendente' else 'Atrasado',
                    'url_comprovante': url_comprovante,
                    'observacoes': pagamento.observacoes if pagamento else None,
                    'data_cadastro': pagamento.data_cadastro.isoformat() if pagamento and pagamento.data_cadastro else None
                })
        
        print(f"✅ Total de registros retornados: {len(resultado)}")
        
        return jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
    except Exception as e:
        import traceback
        print(f"❌ Erro ao listar pagamentos: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ==================== DASHBOARD/ESTATÍSTICAS ====================

@api_bp.route('/dashboard/stats', methods=['GET'])
@api_login_required
def api_dashboard_stats():
    """Estatísticas gerais para dashboard"""
    try:
        # Contar apenas alunos ativos que têm pelo menos uma matrícula ativa (sem data_encerramento)
        # Isso garante que estamos contando alunos que realmente se matricularam
        hoje = date.today()
        
        # Alunos com matrícula ativa (sem data_encerramento ou data_encerramento no futuro)
        alunos_com_matricula = db.session.query(Aluno.id).distinct().join(
            Matricula, Aluno.id == Matricula.aluno_id
        ).filter(
            Aluno.ativo == True,
            db.or_(
                Matricula.data_encerramento.is_(None),
                Matricula.data_encerramento > hoje
            )
        ).subquery()
        
        total_alunos = db.session.query(db.func.count()).select_from(alunos_com_matricula).scalar() or 0
        
        # Para alunos aprovados e pendentes, também considerar apenas os com matrícula ativa
        alunos_aprovados_com_matricula = db.session.query(Aluno.id).distinct().join(
            Matricula, Aluno.id == Matricula.aluno_id
        ).filter(
            Aluno.ativo == True,
            Aluno.aprovado == True,
            db.or_(
                Matricula.data_encerramento.is_(None),
                Matricula.data_encerramento > hoje
            )
        ).count()
        
        alunos_pendentes_com_matricula = db.session.query(Aluno.id).distinct().join(
            Matricula, Aluno.id == Matricula.aluno_id
        ).filter(
            Aluno.ativo == True,
            Aluno.aprovado == False,
            db.or_(
                Matricula.data_encerramento.is_(None),
                Matricula.data_encerramento > hoje
            )
        ).count()
        
        total_professores = Professor.query.filter_by(ativo=True).count()
        alunos_aprovados = alunos_aprovados_com_matricula
        alunos_pendentes = alunos_pendentes_com_matricula
        
        # Alunos com vencimento hoje
        hoje = date.today()
        vencimentos_hoje = Aluno.query.filter(
            Aluno.data_vencimento == hoje,
            Aluno.ativo == True
        ).count()
        
        # Calcular pagamentos atrasados
        # Um pagamento está atrasado se:
        # 1. Não tem pagamento registrado E a data de vencimento já passou
        # 2. OU tem pagamento com status 'rejeitado'
        # 3. OU tem pagamento com status 'pendente' mas a data de vencimento já passou
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Contar alunos ativos sem pagamento e com vencimento passado
        # Considerar apenas alunos com matrícula ativa (mesmo critério do total_alunos)
        alunos_atrasados = 0
        alunos_com_matricula_ativa = db.session.query(Aluno.id).distinct().join(
            Matricula, Aluno.id == Matricula.aluno_id
        ).filter(
            Aluno.ativo == True,
            db.or_(
                Matricula.data_encerramento.is_(None),
                Matricula.data_encerramento > hoje
            )
        ).subquery()
        
        alunos_ativos_ids = [row[0] for row in db.session.query(alunos_com_matricula_ativa.c.id).all()]
        alunos_ativos = Aluno.query.filter(Aluno.id.in_(alunos_ativos_ids)).all() if alunos_ativos_ids else []
        
        for aluno in alunos_ativos:
            if not aluno.data_vencimento:
                continue
            
            # Calcular data de vencimento para o mês atual
            dia_vencimento = aluno.data_vencimento.day
            try:
                data_vencimento_ref = date(ano_atual, mes_atual, dia_vencimento)
            except ValueError:
                ultimo_dia = monthrange(ano_atual, mes_atual)[1]
                data_vencimento_ref = date(ano_atual, mes_atual, min(dia_vencimento, ultimo_dia))
            
            # Buscar pagamento do aluno para o mês atual
            pagamento = Pagamento.query.filter_by(
                aluno_id=aluno.id,
                mes_referencia=mes_atual,
                ano_referencia=ano_atual
            ).first()
            
            # Verificar se está atrasado
            if pagamento:
                # Tem pagamento: verificar status
                if pagamento.status == 'rejeitado':
                    alunos_atrasados += 1
                elif pagamento.status == 'pendente' and data_vencimento_ref < hoje:
                    alunos_atrasados += 1
            else:
                # Não tem pagamento: verificar se vencimento passou
                if data_vencimento_ref < hoje:
                    alunos_atrasados += 1
        
        # Calcular receita mensal (pagamentos aprovados do mês atual)
        # Considerar pagamentos aprovados que foram pagos no mês atual (mes_referencia e ano_referencia)
        receita_mensal_query = db.session.query(
            db.func.sum(Pagamento.valor_pago)
        ).filter(
            Pagamento.status == 'aprovado',
            Pagamento.mes_referencia == hoje.month,
            Pagamento.ano_referencia == hoje.year
        )
        receita_mensal = receita_mensal_query.scalar()
        if receita_mensal is None:
            receita_mensal = 0.0
        else:
            receita_mensal = float(receita_mensal)
        
        return jsonify({
            'success': True,
            'data': {
                'total_alunos': total_alunos,
                'total_professores': total_professores,
                'alunos_aprovados': alunos_aprovados,
                'alunos_pendentes': alunos_pendentes,
                'vencimentos_hoje': vencimentos_hoje,
                'pagamentos_atrasados': int(alunos_atrasados),  # Garantir que é int
                'receita_mensal': float(receita_mensal),  # Campo esperado pelo frontend
                'total_pagamentos': Pagamento.query.count()  # Campo adicional útil
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/alunos-evolucao', methods=['GET'])
@api_login_required
def api_alunos_evolucao():
    """Retorna a evolução do número de alunos nos últimos 12 meses"""
    try:
        from datetime import timedelta
        from calendar import monthrange
        
        hoje = date.today()
        resultado = []
        
        # Gerar os últimos 12 meses
        for i in range(11, -1, -1):  # De 11 meses atrás até hoje
            # Calcular data do mês
            meses_antes = i
            ano = hoje.year
            mes = hoje.month - meses_antes
            
            # Ajustar se o mês for negativo ou zero
            while mes <= 0:
                mes += 12
                ano -= 1
            
            # Último dia do mês
            ultimo_dia = monthrange(ano, mes)[1]
            data_fim_mes = date(ano, mes, ultimo_dia)
            
            # Contar alunos ativos com matrícula ativa até o final daquele mês
            # Considerar alunos que tinham matrícula ativa naquele momento
            alunos_na_epoca = db.session.query(Aluno.id).distinct().join(
                Matricula, Aluno.id == Matricula.aluno_id
            ).filter(
                Aluno.ativo == True,
                # Aluno foi cadastrado até o final daquele mês
                db.func.date(Aluno.data_cadastro) <= data_fim_mes,
                # Matrícula estava ativa naquele momento (sem data_encerramento ou data_encerramento após o fim do mês)
                db.or_(
                    Matricula.data_encerramento.is_(None),
                    Matricula.data_encerramento > data_fim_mes
                ),
                # Matrícula foi criada até o final daquele mês
                db.func.date(Matricula.data_matricula) <= data_fim_mes
            ).count()
            
            meses_nomes = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            
            resultado.append({
                'mes': mes,
                'ano': ano,
                'mes_nome': meses_nomes.get(mes, f'Mês {mes}'),
                'mes_ano': f"{meses_nomes.get(mes, f'Mês {mes}')}/{str(ano)[2:]}",
                'total_alunos': alunos_na_epoca,
                'data_referencia': data_fim_mes.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': resultado
        })
    except Exception as e:
        import traceback
        print(f"❌ Erro ao buscar evolução de alunos: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ==================== NOTAS ====================

@api_bp.route('/notas', methods=['GET'])
@api_login_required
def api_listar_notas():
    """Lista notas (filtros opcionais)"""
    try:
        aluno_id = request.args.get('aluno_id', type=int)
        professor_id = request.args.get('professor_id', type=int)
        tipo_curso = request.args.get('tipo_curso', '').strip()
        
        query = Nota.query
        
        if aluno_id:
            query = query.filter_by(aluno_id=aluno_id)
        
        if professor_id:
            query = query.filter_by(professor_id=professor_id)
        
        if tipo_curso:
            query = query.filter_by(tipo_curso=tipo_curso)
        
        # FILTRAGEM AUTOMÁTICA POR ROLE
        # Professor: só pode ver notas dos seus alunos
        if current_user.is_professor():
            professor = current_user.get_professor()
            if professor:
                query = query.filter_by(professor_id=professor.id)
        # Aluno: só pode ver suas próprias notas
        elif current_user.is_aluno() and current_user.aluno_id:
            query = query.filter_by(aluno_id=current_user.aluno_id)
        # Admin e Gerente: vêem todas as notas
        
        notas = query.order_by(Nota.data_avaliacao.desc()).all()
        
        resultado = []
        for nota in notas:
            resultado.append({
                'id': nota.id,
                'aluno_id': nota.aluno_id,
                'aluno_nome': nota.aluno.nome if nota.aluno else None,
                'professor_id': nota.professor_id,
                'professor_nome': nota.professor.nome if nota.professor else None,
                'tipo_curso': nota.tipo_curso,
                'valor': float(nota.valor) if nota.valor is not None else None,
                'media': nota.calcular_media(),
                'criterio1': float(nota.criterio1) if nota.criterio1 is not None else None,
                'criterio2': float(nota.criterio2) if nota.criterio2 is not None else None,
                'criterio3': float(nota.criterio3) if nota.criterio3 is not None else None,
                'criterio4': float(nota.criterio4) if nota.criterio4 is not None else None,
                'numero_prova': nota.numero_prova,
                'tipo_avaliacao': nota.tipo_avaliacao,
                'observacao': nota.observacao,
                'data_avaliacao': nota.data_avaliacao.isoformat() if nota.data_avaliacao else None,
                'data_cadastro': nota.data_cadastro.isoformat() if nota.data_cadastro else None
            })
        
        return jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notas/<int:nota_id>', methods=['GET'])
@api_login_required
def api_get_nota(nota_id):
    """Busca uma nota específica"""
    try:
        nota = Nota.query.get_or_404(nota_id)
        
        # Verificar permissão se for professor
        if current_user.is_professor():
            professor = current_user.get_professor()
            if not professor or nota.professor_id != professor.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({
            'success': True,
            'data': {
                'id': nota.id,
                'aluno_id': nota.aluno_id,
                'aluno_nome': nota.aluno.nome if nota.aluno else None,
                'professor_id': nota.professor_id,
                'professor_nome': nota.professor.nome if nota.professor else None,
                'matricula_id': nota.matricula_id,
                'tipo_curso': nota.tipo_curso,
                'valor': float(nota.valor) if nota.valor is not None else None,
                'media': nota.calcular_media(),
                'criterio1': float(nota.criterio1) if nota.criterio1 is not None else None,
                'criterio2': float(nota.criterio2) if nota.criterio2 is not None else None,
                'criterio3': float(nota.criterio3) if nota.criterio3 is not None else None,
                'criterio4': float(nota.criterio4) if nota.criterio4 is not None else None,
                'numero_prova': nota.numero_prova,
                'tipo_avaliacao': nota.tipo_avaliacao,
                'observacao': nota.observacao,
                'data_avaliacao': nota.data_avaliacao.isoformat() if nota.data_avaliacao else None,
                'data_cadastro': nota.data_cadastro.isoformat() if nota.data_cadastro else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notas', methods=['POST'])
@api_write_required
def api_criar_nota():
    """Criar nova nota"""
    try:
        data = request.get_json()
        
        aluno_id = data.get('aluno_id')
        professor_id = data.get('professor_id')
        tipo_curso = (data.get('tipo_curso') or '').strip()
        valor = data.get('valor')
        tipo_avaliacao = (data.get('tipo_avaliacao') or '').strip()
        observacao = (data.get('observacao') or '').strip()
        data_avaliacao_str = (data.get('data_avaliacao') or '').strip()
        criterio1 = data.get('criterio1')
        criterio2 = data.get('criterio2')
        criterio3 = data.get('criterio3')
        criterio4 = data.get('criterio4')
        numero_prova = data.get('numero_prova')
        
        # Validações
        if not aluno_id or not professor_id or not tipo_curso:
            return jsonify({'error': 'Aluno, professor e tipo de curso são obrigatórios'}), 400
        
        if valor is None and not any([criterio1, criterio2, criterio3, criterio4]):
            return jsonify({'error': 'Valor ou critérios são obrigatórios'}), 400
        
        if valor is not None and (valor < 0 or valor > 10):
            return jsonify({'error': 'Valor deve estar entre 0 e 10'}), 400
        
        try:
            data_avaliacao = datetime.strptime(data_avaliacao_str, '%Y-%m-%d').date() if data_avaliacao_str else date.today()
        except ValueError:
            return jsonify({'error': 'Data de avaliação inválida'}), 400
        
        nota = Nota(
            aluno_id=aluno_id,
            professor_id=professor_id,
            tipo_curso=tipo_curso,
            valor=valor,
            tipo_avaliacao=tipo_avaliacao if tipo_avaliacao else None,
            observacao=observacao if observacao else None,
            data_avaliacao=data_avaliacao,
            criterio1=criterio1,
            criterio2=criterio2,
            criterio3=criterio3,
            criterio4=criterio4,
            numero_prova=numero_prova,
            cadastrado_por=current_user.id
        )
        
        db.session.add(nota)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nota criada com sucesso',
            'data': {
                'id': nota.id,
                'aluno_nome': nota.aluno.nome if nota.aluno else None,
                'valor': float(nota.valor) if nota.valor else None,
                'media': nota.calcular_media()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notas/<int:nota_id>', methods=['PUT'])
@api_write_required
def api_editar_nota(nota_id):
    """Editar nota existente"""
    try:
        nota = Nota.query.get_or_404(nota_id)
        
        # Verificar permissão
        if current_user.is_professor():
            professor = current_user.get_professor()
            if not professor or nota.professor_id != professor.id:
                return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if 'valor' in data:
            valor = data['valor']
            if valor is not None and (valor < 0 or valor > 10):
                return jsonify({'error': 'Valor deve estar entre 0 e 10'}), 400
            nota.valor = valor
        
        if 'tipo_avaliacao' in data:
            nota.tipo_avaliacao = data['tipo_avaliacao'] or None
        
        if 'observacao' in data:
            nota.observacao = data['observacao'] or None
        
        if 'data_avaliacao' in data:
            try:
                nota.data_avaliacao = datetime.strptime(data['data_avaliacao'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data inválida'}), 400
        
        if 'criterio1' in data:
            nota.criterio1 = data['criterio1']
        if 'criterio2' in data:
            nota.criterio2 = data['criterio2']
        if 'criterio3' in data:
            nota.criterio3 = data['criterio3']
        if 'criterio4' in data:
            nota.criterio4 = data['criterio4']
        if 'numero_prova' in data:
            nota.numero_prova = data['numero_prova']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nota atualizada com sucesso',
            'data': {
                'id': nota.id,
                'valor': float(nota.valor) if nota.valor else None,
                'media': nota.calcular_media()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notas/<int:nota_id>', methods=['DELETE'])
@api_write_required
@api_admin_required
def api_excluir_nota(nota_id):
    """Excluir nota (apenas admin)"""
    try:
        nota = Nota.query.get_or_404(nota_id)
        db.session.delete(nota)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nota excluída com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== CRUD ALUNOS ====================

@api_bp.route('/alunos', methods=['POST'])
@api_write_required
@api_admin_required
def api_criar_aluno():
    """Criar novo aluno"""
    try:
        import traceback
        data = request.get_json()
        print(f"🔍 Dados recebidos para criar aluno: {data}")
        
        # Importar função de normalização
        from app.routes import normalizar_texto
        
        # Campos obrigatórios - garantir que não são None e normalizar nomes
        try:
            nome = normalizar_texto((data.get('nome') or '').strip())
            print(f"✅ Nome processado: '{nome}'")
        except Exception as e:
            print(f"❌ Erro ao processar nome: {e}")
            raise ValueError(f"Erro ao processar nome: {e}")
        
        try:
            telefone = (data.get('telefone') or '').strip()
            print(f"✅ Telefone processado: '{telefone}'")
        except Exception as e:
            print(f"❌ Erro ao processar telefone: {e}")
            raise ValueError(f"Erro ao processar telefone: {e}")
        
        try:
            cidade = normalizar_texto((data.get('cidade') or '').strip())
            print(f"✅ Cidade processada: '{cidade}'")
        except Exception as e:
            print(f"❌ Erro ao processar cidade: {e}")
            raise ValueError(f"Erro ao processar cidade: {e}")
        
        try:
            estado = (data.get('estado') or '').strip().upper()
            print(f"✅ Estado processado: '{estado}'")
        except Exception as e:
            print(f"❌ Erro ao processar estado: {e}")
            raise ValueError(f"Erro ao processar estado: {e}")
        
        try:
            forma_pagamento = normalizar_texto((data.get('forma_pagamento') or '').strip())
            print(f"✅ Forma de pagamento processada: '{forma_pagamento}'")
        except Exception as e:
            print(f"❌ Erro ao processar forma_pagamento: {e}")
            raise ValueError(f"Erro ao processar forma_pagamento: {e}")
        
        try:
            data_vencimento_str = (data.get('data_vencimento') or '').strip()
            print(f"✅ Data de vencimento processada: '{data_vencimento_str}'")
        except Exception as e:
            print(f"❌ Erro ao processar data_vencimento: {e}")
            raise ValueError(f"Erro ao processar data_vencimento: {e}")
        
        if not all([nome, telefone, cidade, estado, forma_pagamento, data_vencimento_str]):
            response = jsonify({'error': 'Campos obrigatórios: nome, telefone, cidade, estado, forma_pagamento, data_vencimento'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        try:
            data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
        except ValueError as e:
            print(f"❌ Erro ao parsear data_vencimento: {e}")
            response = jsonify({'error': 'Data de vencimento inválida'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Determinar modalidades do aluno baseado nas matrículas
        matriculas = data.get('matriculas', [])
        print(f"🔍 Matrículas recebidas: {matriculas}")
        modalidades_set = set()
        for mat in matriculas:
            modalidade = (mat.get('modalidade') or '').strip()
            if modalidade:
                modalidades_set.add(modalidade)
        
        # Parsear data_nascimento com tratamento de erro
        data_nascimento = None
        if data.get('data_nascimento'):
            try:
                data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            except ValueError as e:
                print(f"⚠️ Erro ao parsear data_nascimento: {e}, continuando sem data de nascimento")
        
        print(f"🔍 Criando aluno: nome={nome}, modalidades={modalidades_set}")
        # Tratar campos opcionais que podem ser None e normalizar nomes
        telefone_responsavel = data.get('telefone_responsavel')
        telefone_responsavel = str(telefone_responsavel).strip() if telefone_responsavel else None
        if telefone_responsavel == '':
            telefone_responsavel = None
        
        nome_responsavel = data.get('nome_responsavel')
        if nome_responsavel:
            nome_responsavel = normalizar_texto(str(nome_responsavel).strip())
            if nome_responsavel == '':
                nome_responsavel = None
        else:
            nome_responsavel = None
        
        aluno = Aluno(
            nome=nome,
            telefone=telefone,
            telefone_responsavel=telefone_responsavel,
            nome_responsavel=nome_responsavel,
            cidade=cidade,
            estado=estado,
            forma_pagamento=forma_pagamento,
            data_vencimento=data_vencimento,
            data_nascimento=data_nascimento,
            dublagem_online='dublagem_online' in modalidades_set,
            dublagem_presencial='dublagem_presencial' in modalidades_set,
            teatro_online='teatro_online' in modalidades_set,
            teatro_presencial='teatro_presencial' in modalidades_set,
            locucao='locucao' in modalidades_set,
            teatro_tv_cinema='teatro_tv_cinema' in modalidades_set,
            musical='musical' in modalidades_set,
            ativo=data.get('ativo', True),
            aprovado=data.get('aprovado', True),
            experimental=data.get('experimental', False)
        )
        
        db.session.add(aluno)
        db.session.flush()  # Para obter o ID do aluno
        print(f"✅ Aluno criado com ID: {aluno.id}")
        
        # Criar usuário automaticamente para o aluno
        senha_usuario = data.get('senha_usuario', '').strip()
        if not senha_usuario:
            # Gerar senha aleatória segura se não fornecida
            import secrets
            import string
            caracteres = string.ascii_letters + string.digits + "!@#$%&*"
            senha_usuario = ''.join(secrets.choice(caracteres) for _ in range(12))
            print(f"⚠️  Senha gerada automaticamente para usuário (não será exibida novamente)")
        
        if len(senha_usuario) < 6:
            response = jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            db.session.rollback()
            return response, 400
        
        # Gerar username único
        username = gerar_username_voxen(nome, role='aluno')
        
        # Verificação adicional: garantir que o username não existe (mesmo após geração)
        # Isso previne race conditions
        contador_verificacao = 0
        username_original = username
        while Usuario.query.filter_by(username=username).first():
            contador_verificacao += 1
            if contador_verificacao == 1:
                # Primeira tentativa: adicionar número
                username = f"{username_original}{contador_verificacao}"
            else:
                # Tentativas subsequentes: incrementar número
                username = f"{username_original}{contador_verificacao}"
            if contador_verificacao > 999:
                # Se chegar a 999, usar timestamp
                username = f"{username_original}_{int(datetime.now().timestamp())}"
                break
        
        # Verificar se já existe usuário para este aluno
        usuario_existente = Usuario.query.filter_by(aluno_id=aluno.id).first()
        if usuario_existente:
            # Atualizar senha se usuário já existe
            usuario_existente.set_password(senha_usuario)
            print(f"✅ Senha do usuário existente atualizada: {usuario_existente.username}")
        else:
            # Tentar criar usuário, com tratamento de duplicatas
            email_usuario = f"{username}@voxen.com"
            tentativas = 0
            usuario_criado = False
            while not usuario_criado and tentativas < 5:
                try:
                    usuario = Usuario(
                        username=username,
                        email=email_usuario,
                        role='aluno',
                        aluno_id=aluno.id,
                        ativo=True
                    )
                    usuario.set_password(senha_usuario)
                    db.session.add(usuario)
                    db.session.flush()  # Verificar se há erro de integridade
                    print(f"✅ Usuário criado para aluno: {username} (senha: {senha_usuario})")
                    usuario_criado = True
                except IntegrityError as e:
                    # Se houver erro de integridade (username duplicado), gerar novo username
                    db.session.rollback()
                    tentativas += 1
                    print(f"⚠️ Username {username} já existe, tentativa {tentativas}/5...")
                    if tentativas < 5:
                        username = f"{username_original}_{int(datetime.now().timestamp())}_{tentativas}"
                        email_usuario = f"{username}@voxen.com"
                    else:
                        # Última tentativa: usar timestamp completo
                        username = f"{username_original}_{int(datetime.now().timestamp())}"
                        email_usuario = f"{username}@voxen.com"
            
            if not usuario_criado:
                raise ValueError(f"Não foi possível criar usuário único após {tentativas} tentativas")
        
        db.session.flush()  # Para garantir que o usuário está salvo antes das matrículas
        
        # Criar matrículas
        for idx, matricula_data in enumerate(matriculas):
            professor_id = matricula_data.get('professor_id')
            modalidade = (matricula_data.get('modalidade') or '').strip()
            valor_mensalidade = matricula_data.get('valor_mensalidade')
            horario_id = matricula_data.get('horario_id')
            data_inicio_str = (matricula_data.get('data_inicio') or '').strip()
            
            print(f"🔍 Processando matrícula {idx + 1}: professor_id={professor_id}, modalidade={modalidade}, horario_id={horario_id}")
            
            if not professor_id or not modalidade:
                print(f"⚠️ Matrícula {idx + 1} ignorada: professor_id ou modalidade faltando")
                continue
            
            # Buscar horário se fornecido
            dia_semana = None
            horario_aula = None
            if horario_id:
                try:
                    from app.models.horario_professor import HorarioProfessor
                    horario = HorarioProfessor.query.get(horario_id)
                    if horario:
                        dia_semana = horario.dia_semana
                        horario_aula = horario.horario_aula
                        print(f"✅ Horário encontrado: {dia_semana} - {horario_aula}")
                    else:
                        print(f"⚠️ Horário {horario_id} não encontrado no banco")
                except Exception as e:
                    print(f"⚠️ Erro ao buscar horário {horario_id}: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            data_inicio = None
            if data_inicio_str:
                try:
                    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                except ValueError as e:
                    print(f"⚠️ Erro ao parsear data_inicio: {e}")
                    pass
            
            # Validar e converter valor_mensalidade (agora obrigatório)
            valor_mensalidade_float = None
            if valor_mensalidade:
                try:
                    # Remover espaços e converter
                    valor_str = str(valor_mensalidade).strip().replace(',', '.')
                    if valor_str:
                        valor_mensalidade_float = float(valor_str)
                        if valor_mensalidade_float < 0:
                            print(f"⚠️ Valor da mensalidade negativo: {valor_mensalidade_float}")
                            raise ValueError("Valor da mensalidade não pode ser negativo")
                        if valor_mensalidade_float == 0:
                            print(f"⚠️ Valor da mensalidade zero: {valor_mensalidade_float}")
                            raise ValueError("Valor da mensalidade deve ser maior que zero")
                except (ValueError, TypeError) as e:
                    print(f"❌ Erro ao converter valor_mensalidade '{valor_mensalidade}': {e}")
                    raise ValueError(f"Valor da mensalidade inválido: {valor_mensalidade}")
            else:
                print(f"❌ Valor da mensalidade não fornecido para matrícula {idx + 1}")
                raise ValueError("Valor da mensalidade é obrigatório")
            
            # Validar que temos os dados mínimos
            if not professor_id or not modalidade:
                print(f"⚠️ Matrícula {idx + 1} ignorada: dados incompletos")
                continue
            
            try:
                matricula = Matricula(
                    aluno_id=aluno.id,
                    professor_id=professor_id,
                    tipo_curso=modalidade,
                    valor_mensalidade=valor_mensalidade_float,
                    dia_semana=dia_semana,
                    horario_aula=horario_aula,
                    data_inicio=data_inicio
                )
                db.session.add(matricula)
                print(f"✅ Matrícula {idx + 1} adicionada: aluno_id={aluno.id}, professor_id={professor_id}, modalidade={modalidade}")
            except Exception as e:
                print(f"❌ Erro ao criar matrícula {idx + 1}: {str(e)}")
                import traceback
                print(traceback.format_exc())
                raise
        
        db.session.commit()
        print(f"✅ Aluno {aluno.id} e matrículas criados com sucesso")
        
        response = jsonify({
            'success': True,
            'message': 'Aluno criado com sucesso',
            'data': {
                'id': aluno.id,
                'nome': aluno.nome
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 201
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Erro ao criar aluno: {str(e)}")
        print(f"❌ Traceback completo:\n{error_trace}")
        db.session.rollback()
        response = jsonify({'error': str(e), 'traceback': error_trace if current_app.config.get('DEBUG') else None})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@api_bp.route('/alunos/<int:aluno_id>', methods=['PUT'])
@api_write_required
@api_admin_required
def api_editar_aluno(aluno_id):
    """Editar aluno existente"""
    try:
        from app.routes import normalizar_texto
        
        aluno = Aluno.query.get_or_404(aluno_id)
        data = request.get_json()
        
        if 'nome' in data and data['nome'] is not None:
            aluno.nome = normalizar_texto(str(data['nome']).strip())
        if 'telefone' in data and data['telefone'] is not None:
            aluno.telefone = str(data['telefone']).strip()
        if 'telefone_responsavel' in data:
            aluno.telefone_responsavel = str(data['telefone_responsavel']).strip() if data['telefone_responsavel'] else None
        if 'nome_responsavel' in data:
            aluno.nome_responsavel = normalizar_texto(str(data['nome_responsavel']).strip()) if data['nome_responsavel'] else None
        if 'cidade' in data and data['cidade'] is not None:
            aluno.cidade = normalizar_texto(str(data['cidade']).strip())
        if 'estado' in data and data['estado'] is not None:
            aluno.estado = str(data['estado']).strip().upper()
        if 'forma_pagamento' in data and data['forma_pagamento'] is not None:
            aluno.forma_pagamento = normalizar_texto(str(data['forma_pagamento']).strip())
        if 'data_vencimento' in data:
            try:
                aluno.data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data de vencimento inválida'}), 400
        if 'data_nascimento' in data:
            aluno.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data['data_nascimento'] else None
        
        if 'ativo' in data:
            aluno.ativo = data['ativo']
        if 'aprovado' in data:
            aluno.aprovado = data['aprovado']
        if 'experimental' in data:
            aluno.experimental = data['experimental']
        
        # Atualizar matrículas se fornecidas
        if 'matriculas' in data:
            matriculas = data.get('matriculas', [])
            
            # Deletar matrículas antigas
            Matricula.query.filter_by(aluno_id=aluno_id).delete()
            
            # Determinar modalidades do aluno baseado nas novas matrículas
            modalidades_set = set()
            for mat in matriculas:
                modalidade = (mat.get('modalidade') or '').strip()
                if modalidade:
                    modalidades_set.add(modalidade)
            
            # Atualizar modalidades do aluno
            aluno.dublagem_online = 'dublagem_online' in modalidades_set
            aluno.dublagem_presencial = 'dublagem_presencial' in modalidades_set
            aluno.teatro_online = 'teatro_online' in modalidades_set
            aluno.teatro_presencial = 'teatro_presencial' in modalidades_set
            aluno.locucao = 'locucao' in modalidades_set
            aluno.teatro_tv_cinema = 'teatro_tv_cinema' in modalidades_set
            aluno.musical = 'musical' in modalidades_set
            
            # Criar novas matrículas
            for matricula_data in matriculas:
                professor_id = matricula_data.get('professor_id')
                modalidade = matricula_data.get('modalidade', '').strip()
                valor_mensalidade = matricula_data.get('valor_mensalidade')
                horario_id = matricula_data.get('horario_id')
                data_inicio_str = (matricula_data.get('data_inicio') or '').strip()
                
                if not professor_id or not modalidade:
                    continue
                
                # Buscar horário se fornecido
                dia_semana = None
                horario_aula = None
                if horario_id:
                    from app.models.horario_professor import HorarioProfessor
                    horario = HorarioProfessor.query.get(horario_id)
                    if horario:
                        dia_semana = horario.dia_semana
                        horario_aula = horario.horario_aula
                
                data_inicio = None
                if data_inicio_str:
                    try:
                        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                matricula = Matricula(
                    aluno_id=aluno_id,
                    professor_id=professor_id,
                    tipo_curso=modalidade,
                    valor_mensalidade=float(valor_mensalidade) if valor_mensalidade else None,
                    dia_semana=dia_semana,
                    horario_aula=horario_aula,
                    data_inicio=data_inicio
                )
                db.session.add(matricula)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Aluno atualizado com sucesso',
            'data': {
                'id': aluno.id,
                'nome': aluno.nome
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alunos/<int:aluno_id>', methods=['DELETE'])
@api_write_required
@api_admin_required
def api_excluir_aluno(aluno_id):
    """Excluir aluno (exclusão lógica)"""
    try:
        aluno = Aluno.query.get_or_404(aluno_id)
        aluno.ativo = False
        aluno.data_exclusao = date.today()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Aluno excluído com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== CRUD PROFESSORES ====================

@api_bp.route('/professores', methods=['POST'])
@api_write_required
@api_admin_required
def api_criar_professor():
    """Criar novo professor com horários vinculados"""
    try:
        from app.models.horario_professor import HorarioProfessor
        from app.routes import normalizar_texto
        
        data = request.get_json()
        
        nome = normalizar_texto(data.get('nome', '').strip())
        telefone = data.get('telefone', '').strip()
        horarios = data.get('horarios', [])  # Array de horários
        
        if not nome or not telefone:
            return jsonify({'error': 'Nome e telefone são obrigatórios'}), 400
        
        # Validação: pelo menos um horário com modalidade obrigatório
        if not horarios or len(horarios) == 0:
            return jsonify({'error': 'Adicione pelo menos um horário de aula com modalidade'}), 400
        
        # Determinar modalidades do professor baseado nos horários cadastrados
        modalidades_professor = set([h.get('modalidade') for h in horarios if h.get('modalidade')])
        dublagem_presencial = 'dublagem_presencial' in modalidades_professor
        dublagem_online = 'dublagem_online' in modalidades_professor
        teatro_presencial = 'teatro_presencial' in modalidades_professor
        teatro_online = 'teatro_online' in modalidades_professor
        musical = 'musical' in modalidades_professor
        locucao = 'locucao' in modalidades_professor
        curso_apresentador = 'curso_apresentador' in modalidades_professor
        # Teatro TV/Cinema pode ser derivado de teatro_presencial ou teatro_online
        teatro_tv_cinema = 'teatro_tv_cinema' in modalidades_professor or teatro_presencial or teatro_online
        
        professor = Professor(
            nome=nome,
            telefone=telefone,
            dublagem_online=dublagem_online,
            dublagem_presencial=dublagem_presencial,
            teatro_online=teatro_online,
            teatro_presencial=teatro_presencial,
            locucao=locucao,
            teatro_tv_cinema=teatro_tv_cinema,
            musical=musical,
            curso_apresentador=curso_apresentador,
            ativo=data.get('ativo', True)
        )
        
        db.session.add(professor)
        db.session.flush()  # Para obter o ID do professor
        
        # Criar usuário automaticamente para o professor
        senha_usuario = data.get('senha_usuario', '').strip()
        if not senha_usuario:
            # Gerar senha aleatória segura se não fornecida
            import secrets
            import string
            caracteres = string.ascii_letters + string.digits + "!@#$%&*"
            senha_usuario = ''.join(secrets.choice(caracteres) for _ in range(12))
            print(f"⚠️  Senha gerada automaticamente para usuário (não será exibida novamente)")
        
        if len(senha_usuario) < 6:
            db.session.rollback()
            return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
        # Gerar username único
        username = gerar_username_voxen(nome, role='professor')
        
        # Verificação adicional: garantir que o username não existe (mesmo após geração)
        # Isso previne race conditions
        contador_verificacao = 0
        username_original = username
        while Usuario.query.filter_by(username=username).first():
            contador_verificacao += 1
            if contador_verificacao == 1:
                # Primeira tentativa: adicionar número
                username = f"{username_original}{contador_verificacao}"
            else:
                # Tentativas subsequentes: incrementar número
                username = f"{username_original}{contador_verificacao}"
            if contador_verificacao > 999:
                # Se chegar a 999, usar timestamp
                username = f"{username_original}_{int(datetime.now().timestamp())}"
                break
        
        # Verificar se já existe usuário para este professor
        usuario_existente = Usuario.query.filter_by(professor_id=professor.id).first()
        if usuario_existente:
            # Atualizar senha se usuário já existe
            usuario_existente.set_password(senha_usuario)
            print(f"✅ Senha do usuário existente atualizada: {usuario_existente.username}")
        else:
            # Tentar criar usuário, com tratamento de duplicatas
            email_usuario = f"{username}@voxen.com"
            tentativas = 0
            usuario_criado = False
            while not usuario_criado and tentativas < 5:
                try:
                    usuario = Usuario(
                        username=username,
                        email=email_usuario,
                        role='professor',
                        professor_id=professor.id,
                        ativo=True
                    )
                    usuario.set_password(senha_usuario)
                    db.session.add(usuario)
                    db.session.flush()  # Verificar se há erro de integridade
                    print(f"✅ Usuário criado para professor: {username} (senha: {senha_usuario})")
                    usuario_criado = True
                except IntegrityError as e:
                    # Se houver erro de integridade (username duplicado), gerar novo username
                    db.session.rollback()
                    tentativas += 1
                    print(f"⚠️ Username {username} já existe, tentativa {tentativas}/5...")
                    if tentativas < 5:
                        username = f"{username_original}_{int(datetime.now().timestamp())}_{tentativas}"
                        email_usuario = f"{username}@voxen.com"
                    else:
                        # Última tentativa: usar timestamp completo
                        username = f"{username_original}_{int(datetime.now().timestamp())}"
                        email_usuario = f"{username}@voxen.com"
            
            if not usuario_criado:
                raise ValueError(f"Não foi possível criar usuário único após {tentativas} tentativas")
        
        db.session.flush()  # Para garantir que o usuário está salvo antes dos horários
        
        # Criar horários do professor
        for horario_data in horarios:
            dia_semana = (horario_data.get('dia_semana') or '').strip()
            modalidade = (horario_data.get('modalidade') or '').strip()
            horario_inicio = (horario_data.get('horario_inicio') or '').strip()
            horario_termino = (horario_data.get('horario_termino') or '').strip()
            
            if not dia_semana or not modalidade or not horario_inicio or not horario_termino:
                continue
            
            # Formatar horário como "HH:MM às HH:MM"
            horario_aula = f"{horario_inicio} às {horario_termino}"
            
            horario = HorarioProfessor(
                professor_id=professor.id,
                dia_semana=dia_semana,
                modalidade=modalidade,
                horario_aula=horario_aula,
                idade_minima=horario_data.get('idade_minima') if horario_data.get('idade_minima') else None,
                idade_maxima=horario_data.get('idade_maxima') if horario_data.get('idade_maxima') else None
            )
            db.session.add(horario)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Professor criado com sucesso',
            'data': {
                'id': professor.id,
                'nome': professor.nome
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/professores/<int:professor_id>', methods=['PUT'])
@api_write_required
@api_admin_required
def api_editar_professor(professor_id):
    """Editar professor existente com horários vinculados"""
    try:
        from app.models.horario_professor import HorarioProfessor
        from app.routes import normalizar_texto
        
        professor = Professor.query.get_or_404(professor_id)
        data = request.get_json()
        
        if 'nome' in data and data['nome'] is not None:
            professor.nome = normalizar_texto(str(data['nome']).strip())
        if 'telefone' in data and data['telefone'] is not None:
            professor.telefone = str(data['telefone']).strip()
        
        # Se horários foram enviados, atualizar
        if 'horarios' in data:
            horarios = data.get('horarios', [])
            
            # Validação: pelo menos um horário com modalidade obrigatório
            if not horarios or len(horarios) == 0:
                return jsonify({'error': 'Adicione pelo menos um horário de aula com modalidade'}), 400
            
            # Deletar horários antigos
            HorarioProfessor.query.filter_by(professor_id=professor.id).delete()
            
            # Criar novos horários
            for horario_data in horarios:
                dia_semana = (horario_data.get('dia_semana') or '').strip()
                modalidade = (horario_data.get('modalidade') or '').strip()
                horario_inicio = (horario_data.get('horario_inicio') or '').strip()
                horario_termino = (horario_data.get('horario_termino') or '').strip()
                
                if not dia_semana or not modalidade or not horario_inicio or not horario_termino:
                    continue
                
                # Formatar horário como "HH:MM às HH:MM"
                horario_aula = f"{horario_inicio} às {horario_termino}"
                
                horario = HorarioProfessor(
                    professor_id=professor.id,
                    dia_semana=dia_semana,
                    modalidade=modalidade,
                    horario_aula=horario_aula,
                    idade_minima=horario_data.get('idade_minima') if horario_data.get('idade_minima') else None,
                    idade_maxima=horario_data.get('idade_maxima') if horario_data.get('idade_maxima') else None
                )
                db.session.add(horario)
            
            # Determinar modalidades do professor baseado nos horários cadastrados
            modalidades_professor = set([h.get('modalidade') for h in horarios if h.get('modalidade')])
            professor.dublagem_presencial = 'dublagem_presencial' in modalidades_professor
            professor.dublagem_online = 'dublagem_online' in modalidades_professor
            professor.teatro_presencial = 'teatro_presencial' in modalidades_professor
            professor.teatro_online = 'teatro_online' in modalidades_professor
            professor.musical = 'musical' in modalidades_professor
            professor.locucao = 'locucao' in modalidades_professor
            professor.curso_apresentador = 'curso_apresentador' in modalidades_professor
            # Teatro TV/Cinema pode ser derivado de teatro_presencial ou teatro_online
            professor.teatro_tv_cinema = 'teatro_tv_cinema' in modalidades_professor or professor.teatro_presencial or professor.teatro_online
        
        if 'ativo' in data:
            professor.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Professor atualizado com sucesso',
            'data': {
                'id': professor.id,
                'nome': professor.nome
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/professores/<int:professor_id>', methods=['DELETE'])
@api_write_required
@api_admin_required
def api_excluir_professor(professor_id):
    """Excluir professor (exclusão lógica)"""
    try:
        professor = Professor.query.get_or_404(professor_id)
        professor.ativo = False
        professor.data_exclusao = date.today()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Professor excluído com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== GERENCIAR PAGAMENTOS ====================

@api_bp.route('/pagamentos/<int:pagamento_id>/aprovar', methods=['PUT'])
@api_login_required
@api_admin_required
def api_aprovar_pagamento(pagamento_id):
    """Aprovar pagamento"""
    try:
        pagamento = Pagamento.query.get_or_404(pagamento_id)
        data = request.get_json()
        
        pagamento.status = 'aprovado'
        pagamento.aprovado_por = current_user.id
        pagamento.data_aprovacao = datetime.now()
        if data.get('observacoes_admin'):
            pagamento.observacoes_admin = str(data['observacoes_admin']).strip() if data.get('observacoes_admin') else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento aprovado com sucesso',
            'data': {
                'id': pagamento.id,
                'status': pagamento.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/pagamentos/<int:pagamento_id>/rejeitar', methods=['PUT'])
@api_login_required
@api_admin_required
def api_rejeitar_pagamento(pagamento_id):
    """Rejeitar pagamento"""
    try:
        pagamento = Pagamento.query.get_or_404(pagamento_id)
        data = request.get_json()
        
        pagamento.status = 'rejeitado'
        pagamento.aprovado_por = current_user.id
        pagamento.data_aprovacao = datetime.now()
        if data.get('observacoes_admin'):
            pagamento.observacoes_admin = str(data['observacoes_admin']).strip() if data.get('observacoes_admin') else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento rejeitado',
            'data': {
                'id': pagamento.id,
                'status': pagamento.status
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/pagamentos/upload', methods=['POST', 'OPTIONS'])
@api_login_required
def api_upload_comprovante():
    """Upload de comprovante de pagamento"""
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Validar credenciais do Cloudinary
        cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
        api_key = current_app.config.get('CLOUDINARY_API_KEY')
        api_secret = current_app.config.get('CLOUDINARY_API_SECRET')
        
        if not api_key or not api_secret:
            response = jsonify({'error': 'Credenciais do Cloudinary não configuradas'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        # Obter dados do formulário
        aluno_id = request.form.get('aluno_id')
        mes_referencia = request.form.get('mes_referencia', '').strip()
        ano_referencia = request.form.get('ano_referencia', '').strip()
        valor_pago = request.form.get('valor_pago', '').strip()
        data_pagamento_str = request.form.get('data_pagamento', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações
        erros = []
        
        if not aluno_id:
            erros.append('ID do aluno é obrigatório')
        else:
            try:
                aluno_id_int = int(aluno_id)
                aluno = Aluno.query.get(aluno_id_int)
                if not aluno:
                    erros.append('Aluno não encontrado')
            except ValueError:
                erros.append('ID do aluno inválido')
        
        if not mes_referencia:
            erros.append('Mês de referência é obrigatório')
        else:
            try:
                mes = int(mes_referencia)
                if mes < 1 or mes > 12:
                    erros.append('Mês deve estar entre 1 e 12')
            except ValueError:
                erros.append('Mês de referência inválido')
        
        if not ano_referencia:
            erros.append('Ano de referência é obrigatório')
        else:
            try:
                ano = int(ano_referencia)
                if ano < 2020 or ano > 2100:
                    erros.append('Ano inválido')
            except ValueError:
                erros.append('Ano de referência inválido')
        
        if not valor_pago:
            erros.append('Valor pago é obrigatório')
        else:
            try:
                valor = float(valor_pago.replace(',', '.'))
                if valor <= 0:
                    erros.append('Valor pago deve ser maior que zero')
            except ValueError:
                erros.append('Valor pago inválido')
        
        data_pagamento = None
        if not data_pagamento_str:
            erros.append('Data do pagamento é obrigatória')
        else:
            try:
                data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()
            except ValueError:
                erros.append('Data do pagamento inválida')
        
        # Validar arquivo
        if 'comprovante' not in request.files:
            erros.append('Comprovante é obrigatório')
        else:
            arquivo = request.files['comprovante']
            if arquivo.filename == '':
                erros.append('Comprovante é obrigatório')
            else:
                # Validar extensão
                extensoes_permitidas = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.webp'}
                nome_arquivo = secure_filename(arquivo.filename)
                _, ext = os.path.splitext(nome_arquivo.lower())
                
                if ext not in extensoes_permitidas:
                    erros.append(f'Formato não permitido. Use: {", ".join(extensoes_permitidas)}')
                
                # Validar tamanho (10MB)
                arquivo.seek(0, os.SEEK_END)
                tamanho = arquivo.tell()
                arquivo.seek(0)
                if tamanho > 10 * 1024 * 1024:  # 10MB
                    erros.append('Arquivo muito grande. Máximo: 10MB')
        
        if erros:
            response = jsonify({'error': '; '.join(erros)})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Verificar se já existe pagamento aprovado para o mesmo mês/ano
        pagamento_existente = Pagamento.query.filter_by(
            aluno_id=aluno_id_int,
            mes_referencia=int(mes_referencia),
            ano_referencia=int(ano_referencia),
            status='aprovado'
        ).first()
        
        if pagamento_existente:
            response = jsonify({'error': f'Já existe um pagamento aprovado para {mes_referencia}/{ano_referencia}'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # Fazer upload para Cloudinary
        try:
            arquivo.seek(0)  # Garantir que está no início
            resultado = cloudinary.uploader.upload(
                arquivo,
                folder=f'comprovantes/{aluno_id_int}',
                resource_type='auto',
                allowed_formats=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'webp']
            )
            
            url_comprovante = resultado.get('secure_url')
            public_id = resultado.get('public_id')
            
        except Exception as e:
            response = jsonify({'error': f'Erro ao fazer upload: {str(e)}'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        # Criar registro de pagamento
        pagamento = Pagamento(
            aluno_id=aluno_id_int,
            mes_referencia=int(mes_referencia),
            ano_referencia=int(ano_referencia),
            valor_pago=float(valor_pago.replace(',', '.')),
            data_pagamento=data_pagamento,
            url_comprovante=url_comprovante,
            public_id=public_id,
            observacoes=observacoes if observacoes else None,
            status='pendente'
        )
        
        db.session.add(pagamento)
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Comprovante enviado com sucesso! Aguardando aprovação.',
            'data': {
                'id': pagamento.id,
                'aluno_id': pagamento.aluno_id,
                'status': pagamento.status
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"❌ Erro ao processar upload: {traceback.format_exc()}")
        response = jsonify({'error': f'Erro ao processar upload: {str(e)}'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# ==================== MATRÍCULAS ====================

@api_bp.route('/matriculas', methods=['GET'])
@api_login_required
def api_listar_matriculas():
    """Lista matrículas (filtros opcionais)"""
    try:
        aluno_id = request.args.get('aluno_id', type=int)
        professor_id = request.args.get('professor_id', type=int)
        tipo_curso = request.args.get('tipo_curso', '').strip()
        
        query = Matricula.query
        
        if aluno_id:
            query = query.filter_by(aluno_id=aluno_id)
        
        if professor_id:
            query = query.filter_by(professor_id=professor_id)
        
        if tipo_curso:
            query = query.filter_by(tipo_curso=tipo_curso)
        
        matriculas = query.order_by(Matricula.data_matricula.desc()).all()
        
        resultado = []
        for mat in matriculas:
            resultado.append({
                'id': mat.id,
                'aluno_id': mat.aluno_id,
                'aluno_nome': mat.aluno.nome if mat.aluno else None,
                'professor_id': mat.professor_id,
                'professor_nome': mat.professor.nome if mat.professor else None,
                'tipo_curso': mat.tipo_curso,
                'valor_mensalidade': float(mat.valor_mensalidade) if mat.valor_mensalidade else None,
                'data_inicio': mat.data_inicio.isoformat() if mat.data_inicio else None,
                'data_encerramento': mat.data_encerramento.isoformat() if mat.data_encerramento else None,
                'dia_semana': mat.dia_semana,
                'horario_aula': mat.horario_aula,
                'data_matricula': mat.data_matricula.isoformat() if mat.data_matricula else None
            })
        
        return jsonify({
            'success': True,
            'count': len(resultado),
            'data': resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/matriculas', methods=['POST'])
@api_login_required
@api_admin_required
def api_criar_matricula():
    """Criar nova matrícula"""
    try:
        data = request.get_json()
        
        aluno_id = data.get('aluno_id')
        professor_id = data.get('professor_id')
        tipo_curso = (data.get('tipo_curso') or '').strip()
        valor_mensalidade = data.get('valor_mensalidade')
        
        if not all([aluno_id, professor_id, tipo_curso]):
            return jsonify({'error': 'Aluno, professor e tipo de curso são obrigatórios'}), 400
        
        matricula = Matricula(
            aluno_id=aluno_id,
            professor_id=professor_id,
            tipo_curso=tipo_curso,
            valor_mensalidade=valor_mensalidade,
            data_inicio=datetime.strptime(data['data_inicio'], '%Y-%m-%d').date() if data.get('data_inicio') else None,
            dia_semana=(data.get('dia_semana') or '').strip() or None,
            horario_aula=(data.get('horario_aula') or '').strip() or None
        )
        
        db.session.add(matricula)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Matrícula criada com sucesso',
            'data': {
                'id': matricula.id,
                'aluno_nome': matricula.aluno.nome if matricula.aluno else None,
                'professor_nome': matricula.professor.nome if matricula.professor else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/matriculas/<int:matricula_id>', methods=['PUT'])
@api_login_required
@api_admin_required
def api_editar_matricula(matricula_id):
    """Editar matrícula existente"""
    try:
        matricula = Matricula.query.get_or_404(matricula_id)
        data = request.get_json()
        
        if 'professor_id' in data:
            matricula.professor_id = data['professor_id']
        if 'valor_mensalidade' in data:
            matricula.valor_mensalidade = data['valor_mensalidade']
        if 'data_inicio' in data:
            matricula.data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date() if data['data_inicio'] else None
        if 'dia_semana' in data:
            matricula.dia_semana = str(data['dia_semana']).strip() if data['dia_semana'] else None
        if 'horario_aula' in data:
            matricula.horario_aula = str(data['horario_aula']).strip() if data['horario_aula'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Matrícula atualizada com sucesso',
            'data': {
                'id': matricula.id
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/matriculas/<int:matricula_id>', methods=['DELETE'])
@api_login_required
@api_admin_required
def api_excluir_matricula(matricula_id):
    """Excluir matrícula (encerrar)"""
    try:
        matricula = Matricula.query.get_or_404(matricula_id)
        matricula.data_encerramento = date.today()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Matrícula encerrada com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

