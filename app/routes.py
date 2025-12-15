from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.professor import db, Professor
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.models.horario_professor import HorarioProfessor
from app.models.nota import Nota
from app.models.nota import Nota
from datetime import datetime, date
from sqlalchemy import text
from functools import wraps
import re

bp = Blueprint('main', __name__)

# Decorador para verificar se o usuário é admin
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar se o usuário é professor
def professor_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_professor():
            flash('Acesso negado. Apenas professores podem acessar esta página.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Lista de motivos de exclusão
MOTIVOS_EXCLUSAO = [
    'Desistência do aluno',
    'Inadimplência',
    'Transferência',
    'Término do curso',
    'Problemas de saúde',
    'Mudança de cidade',
    'Não adaptação ao curso',
    'Outro motivo'
]

def normalizar_texto(texto):
    """
    Normaliza texto: primeira letra de cada palavra maiúscula, resto minúscula.
    Retorna string vazia se o texto for None ou vazio.
    """
    if not texto or not texto.strip():
        return texto.strip() if texto else ''
    
    # Dividir em palavras, normalizar cada uma e juntar novamente
    palavras = texto.strip().split()
    palavras_normalizadas = []
    
    for palavra in palavras:
        if palavra:
            # Primeira letra maiúscula, resto minúscula
            palavra_normalizada = palavra[0].upper() + palavra[1:].lower() if len(palavra) > 1 else palavra.upper()
            palavras_normalizadas.append(palavra_normalizada)
    
    return ' '.join(palavras_normalizadas)

def validar_telefone(telefone):
    """Valida o formato do telefone internacional (+DDI DDD Número)"""
    if not telefone:
        return False, "Telefone é obrigatório."
    # Formato: +DDI DDD Número (ex: +55 11 987654321)
    if not re.fullmatch(r'^\+[0-9]{1,3} [0-9]{2} [0-9]{8,9}$', telefone.strip()):
        return False, "Telefone deve estar no formato +DDI DDD Número (ex: +55 11 987654321)."
    return True, ""

@bp.route('/')
def index():
    """Página inicial - redireciona baseado no perfil do usuário"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('main.listar_alunos'))
        elif current_user.is_professor():
            return redirect(url_for('main.listar_alunos'))
        else:
            return redirect(url_for('main.cadastro_alunos'))
    return redirect(url_for('main.login'))

@bp.route('/criar-admin-inicial', methods=['GET', 'POST'])
def criar_admin_inicial():
    """
    Rota temporária para criar o usuário admin inicial.
    Só funciona se a variável de ambiente ENABLE_ADMIN_CREATION estiver configurada.
    Após criar o admin, desative esta variável por segurança!
    """
    import os
    from werkzeug.security import generate_password_hash
    
    # Verificar se a rota está habilitada
    if not os.environ.get('ENABLE_ADMIN_CREATION'):
        flash('Esta rota não está habilitada. Configure ENABLE_ADMIN_CREATION para usar.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        username = request.form.get('username', 'admin').strip()
        senha = request.form.get('senha', '').strip()
        token = request.form.get('token', '').strip()
        
        # Verificar token de segurança (opcional, mas recomendado)
        expected_token = os.environ.get('ADMIN_CREATION_TOKEN', '')
        if expected_token and token != expected_token:
            flash('Token de segurança inválido.', 'error')
            return render_template('criar_admin.html')
        
        if not username:
            flash('Username é obrigatório.', 'error')
            return render_template('criar_admin.html')
        
        if not senha or len(senha) < 6:
            flash('Senha é obrigatória e deve ter pelo menos 6 caracteres.', 'error')
            return render_template('criar_admin.html')
        
        try:
            # Verificar se o usuário já existe
            usuario = Usuario.query.filter_by(username=username).first()
            
            if usuario:
                # Atualizar senha e garantir que é admin
                usuario.set_password(senha)
                usuario.role = 'admin'
                usuario.ativo = True
                db.session.commit()
                flash(f'Usuário "{username}" atualizado com sucesso! Você já pode fazer login.', 'success')
            else:
                # Criar novo usuário admin
                usuario = Usuario(
                    username=username,
                    email=f'{username}@controle-dublagem.com',
                    role='admin',
                    ativo=True
                )
                usuario.set_password(senha)
                db.session.add(usuario)
                db.session.commit()
                flash(f'Usuário administrador "{username}" criado com sucesso! Você já pode fazer login.', 'success')
            
            # Redirecionar para login
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar/atualizar usuário admin: {str(e)}', 'error')
            admin_creation_token = os.environ.get('ADMIN_CREATION_TOKEN', '')
            return render_template('criar_admin.html', admin_creation_token=admin_creation_token)
    
    # Verificar se há token configurado
    admin_creation_token = os.environ.get('ADMIN_CREATION_TOKEN', '')
    return render_template('criar_admin.html', admin_creation_token=admin_creation_token)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Por favor, preencha todos os campos.', 'error')
                return render_template('login.html')
            
            # Buscar usuário por username ou email
            usuario = Usuario.query.filter(
                (Usuario.username == username) | (Usuario.email == username)
            ).first()
            
            if usuario and usuario.check_password(password) and usuario.ativo:
                login_user(usuario)
                try:
                    usuario.ultimo_acesso = datetime.now()
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    import traceback
                    print(f"Erro ao atualizar ultimo_acesso: {traceback.format_exc()}")
                    # Continuar mesmo se houver erro ao atualizar ultimo_acesso
                
                flash(f'Bem-vindo, {usuario.username}!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    try:
                        return redirect(url_for('main.index'))
                    except Exception as e:
                        import traceback
                        print(f"Erro ao redirecionar após login: {traceback.format_exc()}")
                        flash(f'Login realizado com sucesso, mas houve um erro ao redirecionar: {str(e)}', 'warning')
                        return render_template('login.html')
            else:
                flash('Usuário ou senha incorretos, ou conta inativa.', 'error')
        
        return render_template('login.html')
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na rota de login: {error_details}")
        flash(f'Erro interno ao processar login: {str(e)}', 'error')
        return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/cadastro-usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    """Página de cadastro de usuário (apenas para alunos)"""
    if current_user.is_authenticated:
        flash('Você já está logado. Faça logout para criar uma nova conta.', 'info')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validações
        erros = []
        
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        elif len(username) < 3:
            erros.append('Nome de usuário deve ter pelo menos 3 caracteres.')
        elif Usuario.query.filter_by(username=username).first():
            erros.append('Este nome de usuário já está em uso.')
        
        if not email:
            erros.append('Email é obrigatório.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            erros.append('Email inválido.')
        elif Usuario.query.filter_by(email=email).first():
            erros.append('Este email já está cadastrado.')
        
        if not password:
            erros.append('Senha é obrigatória.')
        elif len(password) < 6:
            erros.append('Senha deve ter pelo menos 6 caracteres.')
        elif password != password_confirm:
            erros.append('As senhas não coincidem.')
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
            return render_template('cadastro_usuario.html')
        
        # Criar usuário (sempre como aluno)
        try:
            usuario = Usuario(
                username=username,
                email=email,
                role='aluno',
                ativo=True
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            return render_template('cadastro_usuario.html')
    
    return render_template('cadastro_usuario.html')

@bp.route('/cadastro-professores', methods=['GET', 'POST'])
@admin_required
def cadastro_professores():
    if request.method == 'POST':
        try:
            professores_data = request.form.getlist('professores[]')
            
            if not professores_data:
                flash('Nenhum professor foi enviado.', 'error')
                return render_template('cadastro_professores.html')
            
            professores_cadastrados = 0
            erros = []
            
            # Processar cada professor do formulário
            for i, professor_data in enumerate(professores_data):
                # Obter dados do professor
                nome = normalizar_texto(request.form.get(f'nome_{i}', '').strip())
                telefone = request.form.get(f'telefone_{i}', '').strip()
                
                # Coletar horários do professor (múltiplos horários possíveis)
                horarios_professor = []
                horario_keys = [key for key in request.form.keys() if key.startswith(f'horario_dia_{i}_')]
                for key in horario_keys:
                    horario_index = key.split('_')[-1]
                    dia_semana = request.form.get(f'horario_dia_{i}_{horario_index}', '').strip()
                    horario_inicio = request.form.get(f'horario_inicio_{i}_{horario_index}', '').strip()
                    horario_termino = request.form.get(f'horario_termino_{i}_{horario_index}', '').strip()
                    
                    if dia_semana and horario_inicio and horario_termino:
                        # Formatar horário como "HH:MM às HH:MM"
                        horario_aula = f"{horario_inicio} às {horario_termino}"
                        horarios_professor.append({
                            'dia_semana': dia_semana,
                            'horario_aula': horario_aula
                        })
                
                # Validação: telefone obrigatório e formato
                if not telefone:
                    erros.append(f'Professor {i+1}: Telefone é obrigatório.')
                    continue
                
                # Validar formato do telefone internacional
                valido, msg = validar_telefone(telefone)
                if not valido:
                    erros.append(f'Professor {i+1}: {msg}')
                    continue
                
                telefone = telefone.strip()
                
                # Modalidades
                dublagem_presencial = request.form.get(f'dublagem_presencial_{i}') == 'on'
                dublagem_online = request.form.get(f'dublagem_online_{i}') == 'on'
                teatro_presencial = request.form.get(f'teatro_presencial_{i}') == 'on'
                teatro_online = request.form.get(f'teatro_online_{i}') == 'on'
                musical = request.form.get(f'musical_{i}') == 'on'
                locucao = request.form.get(f'locucao_{i}') == 'on'
                curso_apresentador = request.form.get(f'curso_apresentador_{i}') == 'on'
                
                # Validação: nome obrigatório
                if not nome:
                    erros.append(f'Professor {i+1}: Nome é obrigatório.')
                    continue
                
                # Validação: pelo menos uma modalidade obrigatória
                tem_modalidade = (dublagem_presencial or dublagem_online or teatro_presencial or 
                                teatro_online or musical or locucao or curso_apresentador)
                if not tem_modalidade:
                    erros.append(f'Professor {i+1} ({nome}): Selecione pelo menos uma modalidade.')
                    continue
                
                # Verificar se o professor já existe (mesmo nome e telefone) - apenas ativos
                professor_existente = Professor.query.filter_by(
                    nome=nome,
                    telefone=telefone,
                    ativo=True
                ).first()
                
                if professor_existente:
                    erros.append(f'Professor {i+1} ({nome}): Já existe um professor cadastrado com este nome e telefone.')
                    continue
                
                # Criar e salvar professor (sempre ativo por padrão)
                try:
                    professor = Professor(
                        nome=nome,
                        telefone=telefone,
                        dublagem_presencial=dublagem_presencial,
                        dublagem_online=dublagem_online,
                        teatro_presencial=teatro_presencial,
                        teatro_online=teatro_online,
                        musical=musical,
                        locucao=locucao,
                        curso_apresentador=curso_apresentador,
                        ativo=True
                    )
                    db.session.add(professor)
                    db.session.flush()  # Para obter o ID do professor
                    
                    # Criar horários do professor
                    for horario_data in horarios_professor:
                        horario = HorarioProfessor(
                            professor_id=professor.id,
                            dia_semana=horario_data['dia_semana'],
                            horario_aula=horario_data['horario_aula']
                        )
                        db.session.add(horario)
                    
                    professores_cadastrados += 1
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Erro ao criar professor {i+1} ({nome}): {error_details}")
                    erros.append(f'Professor {i+1} ({nome}): Erro ao cadastrar - {str(e)}')
                    db.session.rollback()
            
            if erros:
                # Se houver erros, fazer rollback antes de retornar
                db.session.rollback()
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro_professores.html')
            
            if professores_cadastrados > 0:
                try:
                    db.session.commit()
                    flash(f'{professores_cadastrados} professor(es) cadastrado(s) com sucesso!', 'success')
                except Exception as e:
                    db.session.rollback()
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Erro ao salvar professores: {error_details}")
                    flash(f'Erro ao salvar no banco de dados: {str(e)}', 'error')
            else:
                # Se nenhum professor foi cadastrado e não há erros, pode ser um problema
                flash('Nenhum professor foi processado. Verifique os dados e tente novamente.', 'error')
            
            return redirect(url_for('main.cadastro_professores'))
        
        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro geral no cadastro de professores: {error_details}")
            flash(f'Erro interno ao processar cadastro: {str(e)}', 'error')
            return render_template('cadastro_professores.html')
    
    return render_template('cadastro_professores.html')

@bp.route('/professores')
@admin_required
def listar_professores():
    # Por padrão, mostrar apenas professores ativos
    filtro = request.args.get('filtro', 'ativos')
    
    if filtro == 'inativos':
        professores = Professor.query.filter_by(ativo=False).order_by(Professor.data_exclusao.desc(), Professor.nome).all()
    else:
        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
    
    # Verificar quais professores já têm usuário cadastrado
    professores_com_usuario = {}
    for professor in professores:
        usuario = Usuario.query.filter_by(professor_id=professor.id).first()
        professores_com_usuario[professor.id] = usuario is not None
    
    return render_template('listar_professores.html', 
                         professores=professores, 
                         filtro=filtro, 
                         motivos_exclusao=MOTIVOS_EXCLUSAO,
                         professores_com_usuario=professores_com_usuario)

@bp.route('/professores/<int:professor_id>/excluir', methods=['POST'])
@admin_required
def excluir_professor(professor_id):
    """Exclusão lógica de professor"""
    professor = Professor.query.get_or_404(professor_id)
    
    motivo = request.form.get('motivo_exclusao', '').strip()
    
    if not motivo:
        flash('Motivo da exclusão é obrigatório.', 'error')
        return redirect(url_for('main.listar_professores'))
    
    professor.ativo = False
    professor.data_exclusao = date.today()
    professor.motivo_exclusao = motivo
    
    try:
        db.session.commit()
        flash(f'Professor {professor.nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir professor: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_professores'))

@bp.route('/professores/<int:professor_id>/reativar', methods=['POST'])
@admin_required
def reativar_professor(professor_id):
    """Reativar professor (reverter exclusão lógica)"""
    professor = Professor.query.get_or_404(professor_id)
    
    professor.ativo = True
    professor.data_exclusao = None
    professor.motivo_exclusao = None
    
    try:
        db.session.commit()
        flash(f'Professor {professor.nome} reativado com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar professor: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_professores', filtro='inativos'))

@bp.route('/cadastro-usuario-professor', methods=['GET', 'POST'])
@admin_required
def cadastro_usuario_professor():
    """Página de cadastro de usuário professor (apenas para admin)"""
    # Se veio com professor_id na query string, pré-selecionar
    professor_id_pre_selecionado = request.args.get('professor_id', '')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        professor_id = request.form.get('professor_id', '').strip()
        
        # Validações
        erros = []
        
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        elif len(username) < 3:
            erros.append('Nome de usuário deve ter pelo menos 3 caracteres.')
        elif Usuario.query.filter_by(username=username).first():
            erros.append('Este nome de usuário já está em uso.')
        
        if not email:
            erros.append('Email é obrigatório.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            erros.append('Email inválido.')
        elif Usuario.query.filter_by(email=email).first():
            erros.append('Este email já está cadastrado.')
        
        if not password:
            erros.append('Senha é obrigatória.')
        elif len(password) < 6:
            erros.append('Senha deve ter pelo menos 6 caracteres.')
        elif password != password_confirm:
            erros.append('As senhas não coincidem.')
        
        if not professor_id:
            erros.append('É obrigatório selecionar um professor.')
        else:
            try:
                professor_id = int(professor_id)
                professor = Professor.query.filter_by(id=professor_id, ativo=True).first()
                if not professor:
                    erros.append('Professor selecionado não existe ou está inativo.')
                # Verificar se já existe usuário para este professor
                elif Usuario.query.filter_by(professor_id=professor_id).first():
                    erros.append(f'Já existe um usuário cadastrado para o professor {professor.nome}.')
            except ValueError:
                erros.append('ID do professor inválido.')
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
            professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
            return render_template('cadastro_usuario_professor.html', 
                                 professores=professores,
                                 professor_id_pre_selecionado=professor_id_pre_selecionado)
        
        # Criar usuário professor
        try:
            usuario = Usuario(
                username=username,
                email=email,
                role='professor',
                professor_id=professor_id,
                ativo=True
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Usuário professor criado com sucesso para {professor.nome}!', 'success')
            return redirect(url_for('main.listar_professores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
            return render_template('cadastro_usuario_professor.html', 
                                 professores=professores,
                                 professor_id_pre_selecionado=professor_id_pre_selecionado)
    
    # GET - mostrar formulário
    professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
    return render_template('cadastro_usuario_professor.html', 
                         professores=professores, 
                         professor_id_pre_selecionado=professor_id_pre_selecionado)

@bp.route('/api/professores', methods=['GET'])
def api_professores():
    """API para buscar professores baseado nas modalidades selecionadas"""
    tipo_curso = request.args.get('tipo_curso', '').strip()
    
    if not tipo_curso:
        return jsonify([])
    
    # Filtrar apenas professores ativos
    query = Professor.query.filter_by(ativo=True)
    
    # Filtrar professores baseado no tipo de curso
    # SQLite armazena booleanos como INTEGER (0 ou 1), então comparamos com 1
    from sqlalchemy import or_
    
    if tipo_curso == 'dublagem_online':
        query = query.filter(Professor.dublagem_online == 1)
    elif tipo_curso == 'dublagem_presencial':
        query = query.filter(Professor.dublagem_presencial == 1)
    elif tipo_curso == 'teatro_online':
        query = query.filter(Professor.teatro_online == 1)
    elif tipo_curso == 'teatro_presencial':
        query = query.filter(Professor.teatro_presencial == 1)
    elif tipo_curso == 'locucao':
        query = query.filter(Professor.locucao == 1)
    elif tipo_curso == 'musical':
        query = query.filter(Professor.musical == 1)
    elif tipo_curso == 'teatro_tv_cinema':
        # Teatro TV/Cinema pode ser com professor de teatro presencial ou online
        query = query.filter(or_(Professor.teatro_presencial == 1, Professor.teatro_online == 1))
    else:
        # Se nenhum tipo foi especificado, retornar vazio
        return jsonify([])
    
    professores = query.order_by(Professor.nome).all()
    
    # Debug: verificar quantos professores foram encontrados
    total_professores = Professor.query.count()
    print(f"DEBUG API: tipo_curso={tipo_curso}, total_professores_no_banco={total_professores}, encontrados={len(professores)}")
    
    # Se não encontrou nenhum, listar todos os professores para debug
    if len(professores) == 0 and total_professores > 0:
        todos_profs = Professor.query.limit(3).all()
        print(f"  DEBUG: Listando primeiros professores do banco:")
        for p in todos_profs:
            print(f"    - {p.nome}: dublagem_online={p.dublagem_online} (type: {type(p.dublagem_online)}), dublagem_presencial={p.dublagem_presencial}")
            # Testar query manual
            if tipo_curso == 'dublagem_online':
                print(f"      Teste: dublagem_online == 1: {p.dublagem_online == 1}, dublagem_online == True: {p.dublagem_online == True}")
    
    resultado = [{
        'id': p.id,
        'nome': p.nome,
        'dublagem_presencial': p.dublagem_presencial,
        'dublagem_online': p.dublagem_online,
        'teatro_presencial': p.teatro_presencial,
        'teatro_online': p.teatro_online,
        'musical': p.musical,
        'locucao': p.locucao,
        'curso_apresentador': p.curso_apresentador
    } for p in professores]
    
    print(f"DEBUG API: Retornando {len(resultado)} professores")
    return jsonify(resultado)

@bp.route('/api/professor/<int:professor_id>/horarios', methods=['GET'])
def api_horarios_professor(professor_id):
    """API para buscar horários de um professor específico"""
    professor = Professor.query.get_or_404(professor_id)
    
    horarios = []
    for horario in professor.horarios:
        horarios.append({
            'id': horario.id,
            'dia_semana': horario.dia_semana,
            'horario_aula': horario.horario_aula
        })
    
    return jsonify(horarios)

@bp.route('/cadastro-alunos', methods=['GET', 'POST'])
@login_required
def cadastro_alunos():
    # Professores não podem cadastrar alunos
    if current_user.is_professor():
        flash('Acesso negado. Professores não podem cadastrar alunos.', 'error')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        # Coletar todos os índices de alunos do formulário
        indices = set()
        for key in request.form.keys():
            if key.startswith('nome_'):
                try:
                    idx = int(key.split('_')[1])
                    indices.add(idx)
                except (ValueError, IndexError):
                    continue
        
        if not indices:
            flash('Nenhum aluno foi adicionado ao formulário.', 'error')
            return render_template('cadastro_alunos.html')
        
        erros = []
        alunos_cadastrados = 0
        tipos_cursos = ['dublagem_online', 'dublagem_presencial', 'teatro_online', 'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical']
        
        try:
            for i in sorted(indices):
                nome = normalizar_texto(request.form.get(f'nome_{i}', '').strip())
                telefone = request.form.get(f'telefone_{i}', '').strip()
                nome_responsavel = normalizar_texto(request.form.get(f'nome_responsavel_{i}', '').strip())
                telefone_responsavel = request.form.get(f'telefone_responsavel_{i}', '').strip()
                data_nascimento_str = request.form.get(f'data_nascimento_{i}', '').strip()
                idade_str = request.form.get(f'idade_{i}', '').strip()
                lembrar_aniversario_str = request.form.get(f'lembrar_aniversario_{i}', 'nao').strip()
                lembrar_aniversario = lembrar_aniversario_str == 'sim'
                
                # Endereço - apenas cidade e estado (obrigatórios)
                cidade = normalizar_texto(request.form.get(f'cidade_{i}', '').strip())
                estado = request.form.get(f'estado_{i}', '').strip().upper()
                
                # Forma de pagamento e data de vencimento
                forma_pagamento = normalizar_texto(request.form.get(f'forma_pagamento_{i}', '').strip())
                data_vencimento_str = request.form.get(f'data_vencimento_{i}', '').strip()
                data_inicio_str = request.form.get(f'data_inicio_{i}', '').strip()
                
                # Validação: nome obrigatório
                if not nome:
                    erros.append(f'Aluno {i+1}: Nome é obrigatório.')
                    continue
                
                # Validação: nome completo (pelo menos duas palavras)
                palavras_nome = nome.strip().split()
                palavras_nome = [p for p in palavras_nome if p]  # Remove strings vazias
                if len(palavras_nome) < 2:
                    erros.append(f'Aluno {i+1} ({nome}): Nome deve ser completo.')
                    continue
                
                # Validação: telefone obrigatório e formato
                valido, msg = validar_telefone(telefone)
                if not valido:
                    erros.append(f'Aluno {i+1} ({nome}): {msg}')
                    continue
                
                # Manter formato internacional do telefone
                telefone = telefone.strip()
                
                # Validação: cidade obrigatória
                if not cidade:
                    erros.append(f'Aluno {i+1} ({nome}): Cidade é obrigatória.')
                    continue
                
                # Validação: estado obrigatório
                if not estado:
                    erros.append(f'Aluno {i+1} ({nome}): Estado é obrigatório.')
                    continue
                
                if len(estado) != 2:
                    erros.append(f'Aluno {i+1} ({nome}): Estado deve ter 2 caracteres (UF).')
                    continue
                
                # Processar idade (obrigatória)
                idade = None
                if idade_str:
                    try:
                        idade = int(idade_str)
                        if idade < 8:
                            erros.append(f'Aluno {i+1} ({nome}): Idade mínima é 8 anos.')
                            continue
                        if idade > 100:
                            erros.append(f'Aluno {i+1} ({nome}): Idade máxima é 100 anos.')
                            continue
                    except ValueError:
                        erros.append(f'Aluno {i+1} ({nome}): Idade inválida.')
                        continue
                else:
                    erros.append(f'Aluno {i+1} ({nome}): Idade é obrigatória.')
                    continue
                
                # Processar data de nascimento (obrigatória apenas se lembrar_aniversario estiver marcado)
                data_nascimento = None
                if lembrar_aniversario:
                    if not data_nascimento_str:
                        erros.append(f'Aluno {i+1} ({nome}): Data de nascimento é obrigatória quando "Deseja ter seu aniversário lembrado" está marcado.')
                        continue
                if data_nascimento_str:
                    try:
                        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                        # Validar que a data não é no futuro
                        today = date.today()
                        if data_nascimento > today:
                            erros.append(f'Aluno {i+1} ({nome}): Data de nascimento não pode ser no futuro.')
                            continue
                    except ValueError:
                        erros.append(f'Aluno {i+1} ({nome}): Data de nascimento inválida.')
                        continue
                
                # Validação: forma de pagamento obrigatória
                if not forma_pagamento:
                    erros.append(f'Aluno {i+1} ({nome}): Forma de pagamento é obrigatória.')
                    continue
                
                # Validação: data de vencimento obrigatória
                if not data_vencimento_str:
                    erros.append(f'Aluno {i+1} ({nome}): Data de vencimento é obrigatória.')
                    continue
                
                try:
                    data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
                    hoje = date.today()
                    
                    # Validar que a data não é no passado
                    if data_vencimento < hoje:
                        erros.append(f'Aluno {i+1} ({nome}): A data de vencimento não pode ser no passado.')
                        continue
                    
                    # Calcular diferença em dias
                    diff_dias = (data_vencimento - hoje).days
                    
                    if diff_dias > 35:
                        # Calcular data limite (hoje + 35 dias)
                        from datetime import timedelta
                        data_limite = hoje + timedelta(days=35)
                        data_limite_str = data_limite.strftime('%d/%m/%Y')
                        erros.append(f'Aluno {i+1} ({nome}): Data Limite: {data_limite_str}')
                        continue
                except ValueError:
                    erros.append(f'Aluno {i+1} ({nome}): Data de vencimento inválida.')
                    continue
                except Exception as e:
                    erros.append(f'Aluno {i+1} ({nome}): Erro ao validar data de vencimento: {str(e)}')
                    continue
                
                # Validação: data de início obrigatória
                if not data_inicio_str:
                    erros.append(f'Aluno {i+1} ({nome}): Data de início das aulas é obrigatória.')
                    continue
                
                try:
                    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                    hoje = date.today()
                    
                    # Validar que a data não é no passado (permitir hoje)
                    if data_inicio < hoje:
                        erros.append(f'Aluno {i+1} ({nome}): A data de início das aulas não pode ser no passado.')
                        continue
                except ValueError:
                    erros.append(f'Aluno {i+1} ({nome}): Data de início inválida.')
                    continue
                except Exception as e:
                    erros.append(f'Aluno {i+1} ({nome}): Erro ao validar data de início: {str(e)}')
                    continue
                
                # Validação: responsável obrigatório para menores de 16 anos
                if idade is not None and idade < 16:
                    if not nome_responsavel:
                        erros.append(f'Aluno {i+1} ({nome}): Nome do responsável é obrigatório para menores de 16 anos.')
                        continue
                    
                    valido_resp, msg_resp = validar_telefone(telefone_responsavel)
                    if not valido_resp:
                        erros.append(f'Aluno {i+1} ({nome}): {msg_resp}')
                        continue
                    
                    telefone_responsavel = telefone_responsavel.strip()
                
                # Verificar se o aluno já existe (mesmo nome e telefone) - apenas ativos
                aluno_existente = Aluno.query.filter_by(
                    nome=nome,
                    telefone=telefone,
                    ativo=True
                ).first()
                
                if aluno_existente:
                    erros.append(f'Aluno {i+1} ({nome}): Já existe um aluno cadastrado com este nome e telefone.')
                    continue
                
                # Cursos, professores e mensalidades
                cursos_professores = {}
                for tipo_curso in tipos_cursos:
                    if request.form.get(f'{tipo_curso}_{i}') == 'on':
                        professor_id_str = request.form.get(f'professor_{tipo_curso}_{i}', '').strip()
                        mensalidade_str = request.form.get(f'mensalidade_{tipo_curso}_{i}', '').strip()
                        dia_semana = request.form.get(f'dia_semana_{tipo_curso}_{i}', '').strip()
                        horario_aula = request.form.get(f'horario_{tipo_curso}_{i}', '').strip()
                        
                        # Validação: se curso está selecionado, professor é obrigatório
                        if not professor_id_str:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): É obrigatório selecionar um professor para o curso "{nome_curso}".')
                            continue
                        
                        # Validação: dia da semana e horário são obrigatórios
                        if not dia_semana or not horario_aula:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): É obrigatório selecionar dia da semana e horário para o curso "{nome_curso}".')
                            continue
                        
                        try:
                            professor_id = int(professor_id_str)
                            
                            # Mensalidade NÃO é obrigatória no cadastro inicial (será preenchida na aprovação pelo admin)
                            # Mas se for informada, deve ser válida
                            valor_mensalidade = None
                            if mensalidade_str:
                                try:
                                    valor_mensalidade = float(mensalidade_str.replace(',', '.'))
                                    if valor_mensalidade <= 0:
                                        nome_curso = tipo_curso.replace('_', ' ').title()
                                        erros.append(f'Aluno {i+1} ({nome}): A mensalidade para o curso "{nome_curso}" deve ser maior que zero.')
                                        continue
                                except ValueError:
                                    nome_curso = tipo_curso.replace('_', ' ').title()
                                    erros.append(f'Aluno {i+1} ({nome}): Mensalidade inválida para o curso "{nome_curso}".')
                                    continue
                            
                            cursos_professores[tipo_curso] = {
                                'professor_id': professor_id,
                                'valor_mensalidade': valor_mensalidade,  # Pode ser None se não foi informado
                                'dia_semana': dia_semana,
                                'horario_aula': horario_aula
                            }
                        except ValueError:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): Professor inválido para o curso "{nome_curso}".')
                            continue
                
                # Verificar se é aluno experimental
                experimental = request.form.get(f'experimental_{i}') == 'on'
                
                # Criar aluno (sempre ativo por padrão)
                # Se não for admin, marcar como pendente de aprovação
                aprovado = current_user.is_admin() if current_user.is_authenticated else False
                
                aluno = Aluno(
                    nome=nome,
                    telefone=telefone,
                    nome_responsavel=nome_responsavel if nome_responsavel else None,
                    telefone_responsavel=telefone_responsavel if telefone_responsavel else None,
                    data_nascimento=data_nascimento,
                    idade=idade,
                    lembrar_aniversario=lembrar_aniversario,
                    cidade=cidade if cidade else None,
                    estado=estado if estado else None,
                    forma_pagamento=forma_pagamento,
                    data_vencimento=data_vencimento,
                    dublagem_online=request.form.get(f'dublagem_online_{i}') == 'on',
                    dublagem_presencial=request.form.get(f'dublagem_presencial_{i}') == 'on',
                    teatro_online=request.form.get(f'teatro_online_{i}') == 'on',
                    teatro_presencial=request.form.get(f'teatro_presencial_{i}') == 'on',
                    locucao=request.form.get(f'locucao_{i}') == 'on',
                    teatro_tv_cinema=request.form.get(f'teatro_tv_cinema_{i}') == 'on',
                    musical=request.form.get(f'musical_{i}') == 'on',
                    experimental=experimental,
                    ativo=True,
                    aprovado=aprovado
                )
                db.session.add(aluno)
                db.session.flush()  # Persistir para obter o ID do aluno
                # O evento before_insert vai preencher dia_vencimento automaticamente
                
                # Criar matrículas
                for tipo_curso, dados in cursos_professores.items():
                    # Debug: verificar dados antes de criar matrícula
                    print(f"DEBUG CADASTRO: Criando matrícula para curso {tipo_curso}")
                    print(f"DEBUG CADASTRO: professor_id={dados.get('professor_id')}, dia_semana={dados.get('dia_semana')}, horario_aula={dados.get('horario_aula')}, data_inicio={data_inicio}")
                    
                    matricula = Matricula(
                        aluno_id=aluno.id,
                        professor_id=dados['professor_id'],
                        tipo_curso=tipo_curso,
                        valor_mensalidade=dados['valor_mensalidade'],
                        data_inicio=data_inicio,
                        dia_semana=dados.get('dia_semana'),
                        horario_aula=dados.get('horario_aula')
                    )
                    db.session.add(matricula)
                    print(f"DEBUG CADASTRO: Matrícula criada - dia_semana={matricula.dia_semana}, horario_aula={matricula.horario_aula}, data_inicio={matricula.data_inicio}")
                
                alunos_cadastrados += 1
                
                # Se não for admin, mostrar mensagem de pendência
                if not aprovado:
                    flash(f'Aluno {nome} cadastrado com sucesso! Aguardando aprovação do administrador.', 'info')
            
            if erros:
                db.session.rollback()
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro_alunos.html')
            
            db.session.commit()
            if alunos_cadastrados > 0:
                if current_user.is_admin():
                    if alunos_cadastrados == 1:
                        flash('Aluno cadastrado com sucesso!', 'success')
                    else:
                        flash(f'{alunos_cadastrados} alunos cadastrados com sucesso!', 'success')
                else:
                    if alunos_cadastrados == 1:
                        flash('Seu cadastro foi enviado e está aguardando aprovação do administrador.', 'info')
                    else:
                        flash(f'Seus {alunos_cadastrados} cadastros foram enviados e estão aguardando aprovação do administrador.', 'info')
            return redirect(url_for('main.cadastro_alunos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar alunos: {str(e)}', 'error')
            return render_template('cadastro_alunos.html')
    
    return render_template('cadastro_alunos.html')

@bp.route('/alunos')
@login_required
def listar_alunos():
    # Por padrão, mostrar apenas alunos ativos
    filtro = request.args.get('filtro', 'ativos')
    
    # Importar para eager loading
    from sqlalchemy.orm import joinedload, subqueryload
    
    if current_user.is_admin():
        # Admin vê todos os alunos - carregar matrículas com eager loading
        if filtro == 'inativos':
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).filter_by(ativo=False).order_by(Aluno.data_exclusao.desc(), Aluno.nome).all()
        elif filtro == 'pendentes':
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).filter_by(ativo=True, aprovado=False).order_by(Aluno.data_cadastro).all()
        elif filtro == 'experimentais':
            # Filtrar apenas alunos experimentais (experimental=True) que estão ativos
            try:
                alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).filter_by(ativo=True, experimental=True).order_by(Aluno.nome).all()
                print(f"DEBUG: Filtro 'experimentais' - {len(alunos)} alunos encontrados")
            except Exception as e:
                # Se a coluna experimental não existir ainda, retornar lista vazia
                import traceback
                print(f"Erro ao filtrar alunos experimentais: {traceback.format_exc()}")
                alunos = []
        else:
            # Alunos ativos e aprovados que NÃO são experimentais
            try:
                alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).filter_by(ativo=True, aprovado=True, experimental=False).order_by(Aluno.nome).all()
            except Exception as e:
                # Se a coluna experimental não existir ainda, usar filtro antigo
                alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).filter_by(ativo=True, aprovado=True).order_by(Aluno.nome).all()
    elif current_user.is_professor():
        # Professor vê apenas seus próprios alunos (através de Matricula)
        professor = current_user.get_professor()
        if not professor:
            flash('Erro: Usuário professor não está vinculado a um registro de professor.', 'error')
            return redirect(url_for('main.index'))
        
        # Buscar alunos através de matrículas - carregar todas as matrículas do aluno, não apenas as do professor
        if filtro == 'inativos':
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).join(Matricula).filter(
                Matricula.professor_id == professor.id,
                Aluno.ativo == False
            ).order_by(Aluno.data_exclusao.desc(), Aluno.nome).distinct().all()
        else:
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).join(Matricula).filter(
                Matricula.professor_id == professor.id,
                Aluno.ativo == True
            ).order_by(Aluno.nome).distinct().all()
    else:
        # Aluno não pode ver lista
        flash('Acesso negado. Apenas administradores e professores podem ver a lista de alunos.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('listar_alunos.html', alunos=alunos, filtro=filtro, motivos_exclusao=MOTIVOS_EXCLUSAO, data_hoje=date.today())

@bp.route('/alunos/<int:aluno_id>/excluir', methods=['POST'])
@admin_required
def excluir_aluno(aluno_id):
    """Exclusão lógica de aluno"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    motivo = request.form.get('motivo_exclusao', '').strip()
    data_encerramento_str = request.form.get('data_encerramento', '').strip()
    
    if not motivo:
        flash('Motivo da exclusão é obrigatório.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    if not data_encerramento_str:
        flash('Data de encerramento da matrícula é obrigatória.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    try:
        data_encerramento = datetime.strptime(data_encerramento_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data de encerramento inválida.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    aluno.ativo = False
    aluno.data_exclusao = date.today()
    aluno.motivo_exclusao = motivo
    
    # Preencher data de encerramento em todas as matrículas ativas do aluno
    for matricula in aluno.matriculas:
        if not matricula.data_encerramento:  # Só preencher se ainda não tiver data de encerramento
            matricula.data_encerramento = data_encerramento
    
    try:
        db.session.commit()
        flash(f'Aluno {aluno.nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir aluno: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_alunos'))

@bp.route('/alunos/<int:aluno_id>/efetivar', methods=['POST'])
@admin_required
def efetivar_aluno(aluno_id):
    """Efetivar aluno experimental (converter para aluno regular)"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    if not aluno.experimental:
        flash('Este aluno já não é mais experimental.', 'info')
        return redirect(url_for('main.listar_alunos', filtro='experimentais'))
    
    # Converter aluno experimental em aluno regular
    aluno.experimental = False
    aluno.aprovado = True  # Alunos efetivados são automaticamente aprovados
    
    try:
        db.session.commit()
        flash(f'Aluno {aluno.nome} efetivado com sucesso! Ele agora é um aluno regular.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao efetivar aluno: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_alunos', filtro='experimentais'))

@bp.route('/alunos/<int:aluno_id>/reativar', methods=['POST'])
@admin_required
def reativar_aluno(aluno_id):
    """Reativar aluno (reverter exclusão lógica)"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    aluno.ativo = True
    aluno.data_exclusao = None
    aluno.motivo_exclusao = None
    
    try:
        db.session.commit()
        flash(f'Aluno {aluno.nome} reativado com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reativar aluno: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_alunos', filtro='inativos'))

@bp.route('/alunos/<int:aluno_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_aluno(aluno_id):
    """Editar aluno pendente"""
    from sqlalchemy.orm import joinedload, subqueryload
    # Usar subqueryload para garantir que todas as matrículas sejam carregadas
    aluno = Aluno.query.options(subqueryload(Aluno.matriculas).joinedload(Matricula.professor)).get_or_404(aluno_id)
    
    # Debug: verificar se as matrículas foram carregadas
    print(f"DEBUG: Aluno {aluno_id} - Nome: {aluno.nome}")
    print(f"DEBUG: Número de matrículas: {len(aluno.matriculas)}")
    for m in aluno.matriculas:
        print(f"DEBUG: Matrícula - Curso: {m.tipo_curso}, Professor: {m.professor_id}, Dia: {m.dia_semana}, Horário: {m.horario_aula}, Data Início: {m.data_inicio}")
    
    # Verificar se é para efetivar (aluno experimental)
    efetivar = request.args.get('efetivar', '0') == '1'
    
    # Permitir editar alunos pendentes ou experimentais
    if aluno.aprovado and not aluno.experimental:
        flash('Este aluno já foi aprovado. Use a edição normal para modificá-lo.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    if request.method == 'POST':
        # Processar edição (similar ao cadastro, mas atualizando o aluno existente)
        # Por enquanto, vou criar uma versão simplificada que permite editar os campos principais
        try:
            nome = normalizar_texto(request.form.get('nome', '').strip())
            telefone = request.form.get('telefone', '').strip()
            cidade = normalizar_texto(request.form.get('cidade', '').strip())
            estado = request.form.get('estado', '').strip().upper()
            forma_pagamento = normalizar_texto(request.form.get('forma_pagamento', '').strip())
            data_vencimento_str = request.form.get('data_vencimento', '').strip()
            data_inicio_str = request.form.get('data_inicio', '').strip()
            
            # Validações básicas
            professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
            
            if not nome:
                flash('Nome é obrigatório.', 'error')
                return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            
            if not cidade or not estado:
                flash('Cidade e estado são obrigatórios.', 'error')
                return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            
            # Processar data de nascimento e idade
            data_nascimento_str = request.form.get('data_nascimento', '').strip()
            idade_str = request.form.get('idade', '').strip()
            lembrar_aniversario_str = request.form.get('lembrar_aniversario', 'nao').strip()
            lembrar_aniversario = lembrar_aniversario_str == 'sim'
            
            data_nascimento = None
            idade = None
            
            if data_nascimento_str:
                try:
                    data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                    today = date.today()
                    idade = today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))
                    if idade < 0:
                        idade = 0
                except ValueError:
                    flash('Data de nascimento inválida.', 'error')
                    professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                    return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            elif idade_str:
                try:
                    idade = int(idade_str)
                except ValueError:
                    flash('Idade inválida.', 'error')
                    professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                    return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            
            # Atualizar campos básicos
            aluno.nome = nome
            aluno.telefone = telefone
            aluno.cidade = cidade
            aluno.estado = estado
            aluno.forma_pagamento = forma_pagamento
            aluno.data_nascimento = data_nascimento
            aluno.idade = idade
            aluno.lembrar_aniversario = lembrar_aniversario
            
            if data_vencimento_str:
                try:
                    aluno.data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de vencimento inválida.', 'error')
                    professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                    return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            
            # Atualizar cursos (checkboxes)
            aluno.dublagem_online = request.form.get('dublagem_online') == 'on'
            aluno.dublagem_presencial = request.form.get('dublagem_presencial') == 'on'
            aluno.teatro_online = request.form.get('teatro_online') == 'on'
            aluno.teatro_presencial = request.form.get('teatro_presencial') == 'on'
            aluno.locucao = request.form.get('locucao') == 'on'
            aluno.teatro_tv_cinema = request.form.get('teatro_tv_cinema') == 'on'
            aluno.musical = request.form.get('musical') == 'on'
            
            # Processar matrículas (professores e mensalidades)
            # Remover matrículas antigas
            Matricula.query.filter_by(aluno_id=aluno.id).delete()
            
            tipos_cursos = ['dublagem_online', 'dublagem_presencial', 'teatro_online', 'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical']
            for tipo_curso in tipos_cursos:
                if request.form.get(tipo_curso) == 'on':
                    professor_id_str = request.form.get(f'professor_{tipo_curso}', '').strip()
                    mensalidade_str = request.form.get(f'mensalidade_{tipo_curso}', '').strip()
                    dia_semana = request.form.get(f'dia_semana_{tipo_curso}', '').strip()
                    horario_aula = request.form.get(f'horario_{tipo_curso}', '').strip()
                    
                    # Validação: se curso está selecionado, professor é obrigatório
                    if not professor_id_str:
                        nome_curso = tipo_curso.replace('_', ' ').title()
                        flash(f'É obrigatório selecionar um professor para o curso "{nome_curso}".', 'error')
                        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                        return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
                    
                    # Validação: mensalidade é obrigatória na aprovação/edição
                    if not mensalidade_str:
                        nome_curso = tipo_curso.replace('_', ' ').title()
                        flash(f'É obrigatório informar a mensalidade para o curso "{nome_curso}".', 'error')
                        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                        return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
                    
                    # Validação: dia da semana e horário são obrigatórios
                    if not dia_semana or not horario_aula:
                        nome_curso = tipo_curso.replace('_', ' ').title()
                        flash(f'É obrigatório selecionar dia da semana e horário para o curso "{nome_curso}".', 'error')
                        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                        return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
                    
                    try:
                        professor_id = int(professor_id_str)
                        valor_mensalidade = float(mensalidade_str.replace(',', '.'))
                        
                        if valor_mensalidade <= 0:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            flash(f'A mensalidade para o curso "{nome_curso}" deve ser maior que zero.', 'error')
                            professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                            return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
                        
                        data_inicio = None
                        if data_inicio_str:
                            try:
                                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                            except ValueError:
                                pass
                        
                        matricula = Matricula(
                            aluno_id=aluno.id,
                            professor_id=professor_id,
                            tipo_curso=tipo_curso,
                            valor_mensalidade=valor_mensalidade,
                            data_inicio=data_inicio,
                            dia_semana=dia_semana if dia_semana else None,
                            horario_aula=horario_aula if horario_aula else None
                        )
                        db.session.add(matricula)
                    except (ValueError, TypeError) as e:
                        nome_curso = tipo_curso.replace('_', ' ').title()
                        flash(f'Erro ao processar dados do curso "{nome_curso}": {str(e)}', 'error')
                        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                        return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
            
            try:
                # Se foi solicitado efetivar (aluno experimental), efetivar agora
                efetivar_param = request.form.get('efetivar', '0') == '1'
                if efetivar_param and aluno.experimental:
                    aluno.experimental = False
                    aluno.aprovado = True
                    flash(f'Aluno {aluno.nome} atualizado e efetivado com sucesso! Ele agora é um aluno regular.', 'success')
                    filtro_redirect = 'experimentais'
                else:
                    flash(f'Aluno {aluno.nome} atualizado com sucesso!', 'success')
                    filtro_redirect = 'pendentes' if not aluno.aprovado else 'ativos'
                
                db.session.commit()
                return redirect(url_for('main.listar_alunos', filtro=filtro_redirect))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao salvar alterações: {str(e)}', 'error')
                professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
                return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores)
        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro ao atualizar aluno: {error_details}")
            flash(f'Erro ao atualizar aluno: {str(e)}', 'error')
            professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
            return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores, efetivar=efetivar)
    
    # GET - mostrar formulário de edição
    # O aluno já foi carregado com eager loading no início da função
    # Recarregar o aluno para garantir que as matrículas estejam atualizadas
    from sqlalchemy.orm import subqueryload
    aluno = Aluno.query.options(subqueryload(Aluno.matriculas).joinedload(Matricula.professor)).get_or_404(aluno_id)
    
    # Debug: verificar se as matrículas foram carregadas
    print(f"DEBUG: Aluno {aluno_id} - Nome: {aluno.nome}")
    print(f"DEBUG: Número de matrículas: {len(aluno.matriculas)}")
    for m in aluno.matriculas:
        print(f"DEBUG: Matrícula - Curso: {m.tipo_curso}, Professor: {m.professor_id}, Dia: {m.dia_semana}, Horário: {m.horario_aula}, Data Início: {m.data_inicio}")
    
    # Passar flag de efetivar para o template
    try:
        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
        return render_template('editar_aluno_pendente.html', aluno=aluno, professores=professores, efetivar=efetivar)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao carregar formulário de edição: {error_details}")
        flash(f'Erro ao carregar formulário de edição: {str(e)}', 'error')
        return redirect(url_for('main.listar_alunos', filtro='pendentes'))

@bp.route('/alunos/<int:aluno_id>/aprovar', methods=['POST'])
@admin_required
def aprovar_aluno(aluno_id):
    """Aprovar aluno pendente"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    if aluno.aprovado:
        flash('Este aluno já foi aprovado.', 'info')
        return redirect(url_for('main.listar_alunos'))
    
    # Validar que todas as mensalidades foram preenchidas
    tipos_cursos = ['dublagem_online', 'dublagem_presencial', 'teatro_online', 'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical']
    cursos_selecionados = []
    for tipo_curso in tipos_cursos:
        if getattr(aluno, tipo_curso, False):
            cursos_selecionados.append(tipo_curso)
    
    # Verificar se há matrículas e se todas têm mensalidade
    matriculas = Matricula.query.filter_by(aluno_id=aluno.id).all()
    erros = []
    
    for tipo_curso in cursos_selecionados:
        matricula = next((m for m in matriculas if m.tipo_curso == tipo_curso), None)
        if not matricula:
            nome_curso = tipo_curso.replace('_', ' ').title()
            erros.append(f'Curso "{nome_curso}" selecionado mas sem matrícula cadastrada.')
        elif not matricula.valor_mensalidade or matricula.valor_mensalidade <= 0:
            nome_curso = tipo_curso.replace('_', ' ').title()
            erros.append(f'Mensalidade não preenchida ou inválida para o curso "{nome_curso}".')
        elif not matricula.dia_semana or not matricula.horario_aula:
            nome_curso = tipo_curso.replace('_', ' ').title()
            erros.append(f'Dia da semana e horário não preenchidos para o curso "{nome_curso}".')
        elif not matricula.data_inicio:
            nome_curso = tipo_curso.replace('_', ' ').title()
            erros.append(f'Data de início não preenchida para o curso "{nome_curso}".')
    
    if erros:
        flash('Não é possível aprovar o aluno. Corrija os seguintes problemas: ' + ' '.join(erros), 'error')
        return redirect(url_for('main.listar_alunos', filtro='pendentes'))
    
    aluno.aprovado = True
    
    try:
        db.session.commit()
        flash(f'Aluno {aluno.nome} aprovado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar aluno: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_alunos', filtro='pendentes'))

# ==================== ROTAS DE NOTAS ====================

@bp.route('/notas', methods=['GET'])
@login_required
def listar_notas():
    """Lista todas as notas (admin vê todas, professor vê apenas dos seus alunos)"""
    from sqlalchemy.orm import joinedload
    
    # Filtros
    aluno_id = request.args.get('aluno_id', type=int)
    professor_id = request.args.get('professor_id', type=int)
    tipo_curso = request.args.get('tipo_curso', '')
    
    # Base query com eager loading
    query = Nota.query.options(
        joinedload(Nota.aluno),
        joinedload(Nota.professor),
        joinedload(Nota.matricula)
    )
    
    # Se for professor, só pode ver notas dos seus alunos
    if current_user.is_professor():
        professor = current_user.get_professor()
        if not professor:
            flash('Professor não encontrado.', 'error')
            return redirect(url_for('main.index'))
        
        # Buscar IDs dos alunos deste professor através das matrículas
        alunos_ids = db.session.query(Matricula.aluno_id).filter_by(
            professor_id=professor.id
        ).distinct().all()
        alunos_ids = [row[0] for row in alunos_ids]
        
        if not alunos_ids:
            # Professor sem alunos
            return render_template('listar_notas.html', notas=[], alunos=[], professores=[])
        
        query = query.filter(Nota.aluno_id.in_(alunos_ids))
        query = query.filter(Nota.professor_id == professor.id)
    
    # Aplicar filtros adicionais
    if aluno_id:
        query = query.filter(Nota.aluno_id == aluno_id)
    if professor_id and current_user.is_admin():
        query = query.filter(Nota.professor_id == professor_id)
    if tipo_curso:
        query = query.filter(Nota.tipo_curso == tipo_curso)
    
    notas = query.order_by(Nota.data_avaliacao.desc(), Nota.data_cadastro.desc()).all()
    
    # Buscar alunos e professores para filtros (apenas admin)
    alunos = []
    professores = []
    if current_user.is_admin():
        alunos = Aluno.query.filter_by(ativo=True).order_by(Aluno.nome).all()
        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
    elif current_user.is_professor():
        # Professor só vê seus próprios alunos
        professor = current_user.get_professor()
        if professor:
            alunos_ids = db.session.query(Matricula.aluno_id).filter_by(
                professor_id=professor.id
            ).distinct().all()
            alunos_ids = [row[0] for row in alunos_ids]
            if alunos_ids:
                alunos = Aluno.query.filter(
                    Aluno.id.in_(alunos_ids),
                    Aluno.ativo == True
                ).order_by(Aluno.nome).all()
    
    return render_template('listar_notas.html', 
                         notas=notas, 
                         alunos=alunos, 
                         professores=professores,
                         aluno_id=aluno_id,
                         professor_id=professor_id,
                         tipo_curso=tipo_curso)

@bp.route('/notas/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_nota():
    """Cadastrar nova nota (admin pode cadastrar para qualquer aluno, professor apenas para seus alunos)"""
    from sqlalchemy.orm import joinedload
    
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id', type=int)
        professor_id = request.form.get('professor_id', type=int)
        matricula_id = request.form.get('matricula_id', type=int) or None
        tipo_curso = request.form.get('tipo_curso', '').strip()
        valor = request.form.get('valor', type=float)
        observacao = request.form.get('observacao', '').strip()
        data_avaliacao_str = request.form.get('data_avaliacao', '').strip()
        tipo_avaliacao = request.form.get('tipo_avaliacao', '').strip()
        
        # Validações
        if not aluno_id:
            flash('Aluno é obrigatório.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        if not professor_id:
            flash('Professor é obrigatório.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        if not tipo_curso:
            flash('Tipo de curso é obrigatório.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        if valor is None:
            flash('Valor da nota é obrigatório.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        if valor < 0 or valor > 10:
            flash('Valor da nota deve estar entre 0 e 10.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        if not data_avaliacao_str:
            flash('Data da avaliação é obrigatória.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        try:
            data_avaliacao = datetime.strptime(data_avaliacao_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data da avaliação inválida.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        # Verificar se professor pode cadastrar nota para este aluno
        if current_user.is_professor():
            professor = current_user.get_professor()
            if not professor or professor.id != professor_id:
                flash('Você não tem permissão para cadastrar nota para este professor.', 'error')
                return redirect(url_for('main.cadastrar_nota'))
            
            # Verificar se o aluno está matriculado com este professor
            matricula_existe = Matricula.query.filter_by(
                aluno_id=aluno_id,
                professor_id=professor_id,
                tipo_curso=tipo_curso
            ).first()
            
            if not matricula_existe:
                flash('Aluno não está matriculado com você neste curso.', 'error')
                return redirect(url_for('main.cadastrar_nota'))
        
        # Verificar se aluno existe e está ativo
        aluno = Aluno.query.get(aluno_id)
        if not aluno or not aluno.ativo:
            flash('Aluno não encontrado ou inativo.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        # Verificar se professor existe e está ativo
        professor = Professor.query.get(professor_id)
        if not professor or not professor.ativo:
            flash('Professor não encontrado ou inativo.', 'error')
            return redirect(url_for('main.cadastrar_nota'))
        
        # Criar nota
        nota = Nota(
            aluno_id=aluno_id,
            professor_id=professor_id,
            matricula_id=matricula_id,
            tipo_curso=tipo_curso,
            valor=valor,
            observacao=observacao if observacao else None,
            data_avaliacao=data_avaliacao,
            tipo_avaliacao=tipo_avaliacao if tipo_avaliacao else None,
            cadastrado_por=current_user.id
        )
        
        try:
            db.session.add(nota)
            db.session.commit()
            flash(f'Nota cadastrada com sucesso para {aluno.nome}!', 'success')
            return redirect(url_for('main.listar_notas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar nota: {str(e)}', 'error')
            return redirect(url_for('main.cadastrar_nota'))
    
    # GET - mostrar formulário
    aluno_id = request.args.get('aluno_id', type=int)
    professor_id = request.args.get('professor_id', type=int)
    
    # Buscar alunos e professores disponíveis
    alunos = []
    professores = []
    matriculas = []
    
    if current_user.is_admin():
        alunos = Aluno.query.filter_by(ativo=True).order_by(Aluno.nome).all()
        professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
        if aluno_id and professor_id:
            matriculas = Matricula.query.filter_by(
                aluno_id=aluno_id,
                professor_id=professor_id
            ).all()
    elif current_user.is_professor():
        professor = current_user.get_professor()
        if professor:
            # Buscar alunos deste professor
            alunos_ids = db.session.query(Matricula.aluno_id).filter_by(
                professor_id=professor.id
            ).distinct().all()
            alunos_ids = [row[0] for row in alunos_ids]
            
            if alunos_ids:
                alunos = Aluno.query.filter(
                    Aluno.id.in_(alunos_ids),
                    Aluno.ativo == True
                ).order_by(Aluno.nome).all()
            
            professores = [professor]  # Professor só pode cadastrar para si mesmo
            
            if aluno_id:
                matriculas = Matricula.query.filter_by(
                    aluno_id=aluno_id,
                    professor_id=professor.id
                ).all()
    
    tipos_cursos = {
        'dublagem_online': 'Dublagem Online',
        'dublagem_presencial': 'Dublagem Presencial',
        'teatro_online': 'Teatro Online',
        'teatro_presencial': 'Teatro Presencial',
        'locucao': 'Locução',
        'teatro_tv_cinema': 'Teatro TV Cinema',
        'musical': 'Musical'
    }
    
    data_hoje = date.today().isoformat()
    
    return render_template('cadastrar_nota.html',
                         alunos=alunos,
                         professores=professores,
                         matriculas=matriculas,
                         tipos_cursos=tipos_cursos,
                         aluno_id=aluno_id,
                         professor_id=professor_id,
                         data_hoje=data_hoje)

@bp.route('/notas/<int:nota_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_nota(nota_id):
    """Editar nota existente"""
    nota = Nota.query.get_or_404(nota_id)
    
    # Verificar permissão
    if current_user.is_professor():
        professor = current_user.get_professor()
        if not professor or nota.professor_id != professor.id:
            flash('Você não tem permissão para editar esta nota.', 'error')
            return redirect(url_for('main.listar_notas'))
    
    if request.method == 'POST':
        valor = request.form.get('valor', type=float)
        observacao = request.form.get('observacao', '').strip()
        data_avaliacao_str = request.form.get('data_avaliacao', '').strip()
        tipo_avaliacao = request.form.get('tipo_avaliacao', '').strip()
        
        # Validações
        if valor is None:
            flash('Valor da nota é obrigatório.', 'error')
            return redirect(url_for('main.editar_nota', nota_id=nota_id))
        
        if valor < 0 or valor > 10:
            flash('Valor da nota deve estar entre 0 e 10.', 'error')
            return redirect(url_for('main.editar_nota', nota_id=nota_id))
        
        if not data_avaliacao_str:
            flash('Data da avaliação é obrigatória.', 'error')
            return redirect(url_for('main.editar_nota', nota_id=nota_id))
        
        try:
            data_avaliacao = datetime.strptime(data_avaliacao_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data da avaliação inválida.', 'error')
            return redirect(url_for('main.editar_nota', nota_id=nota_id))
        
        # Atualizar nota
        nota.valor = valor
        nota.observacao = observacao if observacao else None
        nota.data_avaliacao = data_avaliacao
        nota.tipo_avaliacao = tipo_avaliacao if tipo_avaliacao else None
        
        try:
            db.session.commit()
            flash('Nota atualizada com sucesso!', 'success')
            return redirect(url_for('main.listar_notas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar nota: {str(e)}', 'error')
            return redirect(url_for('main.editar_nota', nota_id=nota_id))
    
    # GET - mostrar formulário
    tipos_cursos = {
        'dublagem_online': 'Dublagem Online',
        'dublagem_presencial': 'Dublagem Presencial',
        'teatro_online': 'Teatro Online',
        'teatro_presencial': 'Teatro Presencial',
        'locucao': 'Locução',
        'teatro_tv_cinema': 'Teatro TV Cinema',
        'musical': 'Musical'
    }
    
    return render_template('editar_nota.html', nota=nota, tipos_cursos=tipos_cursos)

@bp.route('/notas/<int:nota_id>/excluir', methods=['POST'])
@login_required
def excluir_nota(nota_id):
    """Excluir nota"""
    nota = Nota.query.get_or_404(nota_id)
    
    # Verificar permissão
    if current_user.is_professor():
        professor = current_user.get_professor()
        if not professor or nota.professor_id != professor.id:
            flash('Você não tem permissão para excluir esta nota.', 'error')
            return redirect(url_for('main.listar_notas'))
    
    try:
        aluno_nome = nota.aluno.nome if nota.aluno else 'Aluno'
        db.session.delete(nota)
        db.session.commit()
        flash(f'Nota de {aluno_nome} excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir nota: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_notas'))


