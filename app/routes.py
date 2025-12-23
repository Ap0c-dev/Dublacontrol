from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.professor import db, Professor
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.models.horario_professor import HorarioProfessor
from app.models.nota import Nota
from app.models.nota import Nota
from app.models.pagamento import Pagamento
from datetime import datetime, date, timedelta
from sqlalchemy import text
from functools import wraps
import re
import os
from werkzeug.utils import secure_filename

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
    if not texto:
        return ''
    
    # Converter para string e remover espaços extras
    texto_str = str(texto).strip()
    if not texto_str:
        return ''
    
    # Dividir em palavras, normalizar cada uma e juntar novamente
    palavras = texto_str.split()
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

@bp.route('/test-api')
def test_api_page():
    """Página de teste da API REST"""
    return render_template('test_api.html')

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
                    modalidade = request.form.get(f'horario_modalidade_{i}_{horario_index}', '').strip()
                    horario_inicio = request.form.get(f'horario_inicio_{i}_{horario_index}', '').strip()
                    horario_termino = request.form.get(f'horario_termino_{i}_{horario_index}', '').strip()
                    idade_minima = request.form.get(f'horario_idade_minima_{i}_{horario_index}', '').strip()
                    idade_maxima = request.form.get(f'horario_idade_maxima_{i}_{horario_index}', '').strip()
                    
                    if dia_semana and modalidade and horario_inicio and horario_termino:
                        # Formatar horário como "HH:MM às HH:MM"
                        horario_aula = f"{horario_inicio} às {horario_termino}"
                        horarios_professor.append({
                            'dia_semana': dia_semana,
                            'modalidade': modalidade,
                            'horario_aula': horario_aula,
                            'idade_minima': int(idade_minima) if idade_minima and idade_minima.isdigit() else None,
                            'idade_maxima': int(idade_maxima) if idade_maxima and idade_maxima.isdigit() else None
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
                
                # Validação: nome obrigatório
                if not nome:
                    erros.append(f'Professor {i+1}: Nome é obrigatório.')
                    continue
                
                # Validação: pelo menos um horário com modalidade obrigatório
                if not horarios_professor:
                    erros.append(f'Professor {i+1} ({nome}): Adicione pelo menos um horário de aula com modalidade.')
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
                
                # Determinar modalidades do professor baseado nos horários cadastrados
                modalidades_professor = set([h['modalidade'] for h in horarios_professor])
                dublagem_presencial = 'dublagem_presencial' in modalidades_professor
                dublagem_online = 'dublagem_online' in modalidades_professor
                teatro_presencial = 'teatro_presencial' in modalidades_professor
                teatro_online = 'teatro_online' in modalidades_professor
                musical = 'musical' in modalidades_professor
                locucao = 'locucao' in modalidades_professor
                curso_apresentador = 'curso_apresentador' in modalidades_professor
                # Teatro TV/Cinema pode ser derivado de teatro_presencial ou teatro_online
                teatro_tv_cinema = 'teatro_tv_cinema' in modalidades_professor or teatro_presencial or teatro_online
                
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
                        teatro_tv_cinema=teatro_tv_cinema,
                        ativo=True
                    )
                    db.session.add(professor)
                    db.session.flush()  # Para obter o ID do professor
                    
                    # Criar horários do professor
                    for horario_data in horarios_professor:
                        horario = HorarioProfessor(
                            professor_id=professor.id,
                            dia_semana=horario_data['dia_semana'],
                            modalidade=horario_data['modalidade'],
                            horario_aula=horario_data['horario_aula'],
                            idade_minima=horario_data.get('idade_minima'),
                            idade_maxima=horario_data.get('idade_maxima')
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
    from sqlalchemy.orm import joinedload
    from sqlalchemy import nullslast
    
    try:
        # Por padrão, mostrar apenas professores ativos
        filtro = request.args.get('filtro', 'ativos')
        
        # Tentar carregar com joinedload, mas se falhar, tentar sem
        try:
            if filtro == 'inativos':
                # Usar nullslast() para compatibilidade com PostgreSQL quando data_exclusao é NULL
                # Tentar ordenar por data_exclusao, mas se falhar, ordenar apenas por nome
                try:
                    professores = Professor.query.options(joinedload(Professor.horarios)).filter_by(ativo=False).order_by(nullslast(Professor.data_exclusao.desc()), Professor.nome).all()
                except Exception:
                    # Se a ordenação por data_exclusao falhar, ordenar apenas por nome
                    professores = Professor.query.options(joinedload(Professor.horarios)).filter_by(ativo=False).order_by(Professor.nome).all()
            else:
                professores = Professor.query.options(joinedload(Professor.horarios)).filter_by(ativo=True).order_by(Professor.nome).all()
        except Exception as load_error:
            # Se joinedload falhar (pode ser que a tabela horarios_professor não exista), tentar sem eager loading
            print(f"Erro ao carregar horários com joinedload: {load_error}. Tentando sem eager loading...")
            if filtro == 'inativos':
                try:
                    professores = Professor.query.filter_by(ativo=False).order_by(nullslast(Professor.data_exclusao.desc()), Professor.nome).all()
                except Exception:
                    professores = Professor.query.filter_by(ativo=False).order_by(Professor.nome).all()
            else:
                professores = Professor.query.filter_by(ativo=True).order_by(Professor.nome).all()
            
            # Carregar horários manualmente para cada professor
            for professor in professores:
                try:
                    professor.horarios = HorarioProfessor.query.filter_by(professor_id=professor.id).all()
                except Exception as horario_error:
                    # Se não conseguir carregar horários, usar lista vazia
                    professor.horarios = []
                    print(f"Erro ao carregar horários do professor {professor.id}: {horario_error}")
        
        # Verificar quais professores já têm usuário cadastrado
        professores_com_usuario = {}
        for professor in professores:
            try:
                usuario = Usuario.query.filter_by(professor_id=professor.id).first()
                professores_com_usuario[professor.id] = usuario is not None
            except Exception as e:
                # Se houver erro ao buscar usuário, considerar como não tendo usuário
                professores_com_usuario[professor.id] = False
                print(f"Erro ao verificar usuário do professor {professor.id}: {e}")
        
        return render_template('listar_professores.html', 
                             professores=professores, 
                             filtro=filtro, 
                             motivos_exclusao=MOTIVOS_EXCLUSAO,
                             professores_com_usuario=professores_com_usuario)
    except Exception as e:
        import traceback
        error_msg = f"Erro ao listar professores: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        flash(f'Erro ao carregar lista de professores: {str(e)}', 'error')
        # Retornar lista vazia em caso de erro
        return render_template('listar_professores.html', 
                             professores=[], 
                             filtro=filtro if 'filtro' in locals() else 'ativos', 
                             motivos_exclusao=MOTIVOS_EXCLUSAO,
                             professores_com_usuario={})

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

@bp.route('/professores/<int:professor_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_professor(professor_id):
    """Editar professor existente"""
    professor = Professor.query.get_or_404(professor_id)
    
    if request.method == 'POST':
        try:
            nome = normalizar_texto(request.form.get('nome', '').strip())
            telefone = request.form.get('telefone', '').strip()
            
            # Validação: telefone obrigatório e formato
            if not telefone:
                flash('Telefone é obrigatório.', 'error')
                return render_template('editar_professor.html', professor=professor)
            
            # Validar formato do telefone internacional
            valido, msg = validar_telefone(telefone)
            if not valido:
                flash(msg, 'error')
                return render_template('editar_professor.html', professor=professor)
            
            telefone = telefone.strip()
            
            # Validação: nome obrigatório
            if not nome:
                flash('Nome é obrigatório.', 'error')
                return render_template('editar_professor.html', professor=professor)
            
            # Processar horários
            # Primeiro, remover todos os horários existentes
            HorarioProfessor.query.filter_by(professor_id=professor.id).delete()
            
            # Adicionar novos horários
            horario_keys = [key for key in request.form.keys() if key.startswith('horario_dia_')]
            horarios_adicionados = set()
            
            for key in horario_keys:
                horario_index = key.split('_')[-1]
                dia_semana = request.form.get(f'horario_dia_{horario_index}', '').strip()
                modalidade = request.form.get(f'horario_modalidade_{horario_index}', '').strip()
                horario_inicio = request.form.get(f'horario_inicio_{horario_index}', '').strip()
                horario_termino = request.form.get(f'horario_termino_{horario_index}', '').strip()
                idade_minima = request.form.get(f'horario_idade_minima_{horario_index}', '').strip()
                idade_maxima = request.form.get(f'horario_idade_maxima_{horario_index}', '').strip()
                
                if dia_semana and modalidade and horario_inicio and horario_termino:
                    # Formatar horário como "HH:MM às HH:MM"
                    horario_aula = f"{horario_inicio} às {horario_termino}"
                    
                    # Criar chave única para evitar duplicatas
                    chave_horario = f"{dia_semana}_{modalidade}_{horario_aula}"
                    if chave_horario not in horarios_adicionados:
                        horario = HorarioProfessor(
                            professor_id=professor.id,
                            dia_semana=dia_semana,
                            modalidade=modalidade,
                            horario_aula=horario_aula,
                            idade_minima=int(idade_minima) if idade_minima and idade_minima.isdigit() else None,
                            idade_maxima=int(idade_maxima) if idade_maxima and idade_maxima.isdigit() else None
                        )
                        db.session.add(horario)
                        horarios_adicionados.add(chave_horario)
            
            # Determinar modalidades do professor baseado nos horários que serão cadastrados
            modalidades_professor = set()
            for key in horario_keys:
                horario_index = key.split('_')[-1]
                modalidade = request.form.get(f'horario_modalidade_{horario_index}', '').strip()
                if modalidade:
                    modalidades_professor.add(modalidade)
            
            dublagem_presencial = 'dublagem_presencial' in modalidades_professor
            dublagem_online = 'dublagem_online' in modalidades_professor
            teatro_presencial = 'teatro_presencial' in modalidades_professor
            teatro_online = 'teatro_online' in modalidades_professor
            musical = 'musical' in modalidades_professor
            locucao = 'locucao' in modalidades_professor
            curso_apresentador = 'curso_apresentador' in modalidades_professor
            teatro_tv_cinema = 'teatro_tv_cinema' in modalidades_professor or teatro_presencial or teatro_online
            
            # Atualizar dados do professor
            professor.nome = nome
            professor.telefone = telefone
            professor.dublagem_presencial = dublagem_presencial
            professor.dublagem_online = dublagem_online
            professor.teatro_presencial = teatro_presencial
            professor.teatro_online = teatro_online
            professor.musical = musical
            professor.locucao = locucao
            professor.curso_apresentador = curso_apresentador
            professor.teatro_tv_cinema = teatro_tv_cinema
            
            # Validação: pelo menos um horário com modalidade obrigatório
            if not horarios_adicionados:
                flash('Adicione pelo menos um horário de aula com modalidade.', 'error')
                return render_template('editar_professor.html', professor=professor)
            
            try:
                db.session.commit()
                flash(f'Professor {professor.nome} atualizado com sucesso!', 'success')
                return redirect(url_for('main.listar_professores'))
            except Exception as e:
                db.session.rollback()
                import traceback
                error_details = traceback.format_exc()
                print(f"Erro ao atualizar professor: {error_details}")
                flash(f'Erro ao atualizar professor: {str(e)}', 'error')
        
        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro geral na edição de professor: {error_details}")
            flash(f'Erro interno ao processar edição: {str(e)}', 'error')
    
    # GET - mostrar formulário de edição
    return render_template('editar_professor.html', professor=professor)

@bp.route('/migrar-horarios-professor', methods=['GET'])
@admin_required
def migrar_horarios_professor():
    """Rota temporária para executar migração da tabela horarios_professor"""
    try:
        from sqlalchemy import inspect
        from sqlalchemy import text
        
        # Detectar tipo de banco de dados
        inspector = inspect(db.engine)
        is_postgresql = db.engine.dialect.name == 'postgresql'
        
        # Verificar se a tabela já existe
        tabela_existe = 'horarios_professor' in inspector.get_table_names()
        
        if tabela_existe:
            # Verificar se a coluna modalidade existe
            colunas = [col['name'] for col in inspector.get_columns('horarios_professor')]
            coluna_modalidade_existe = 'modalidade' in colunas
            
            if coluna_modalidade_existe:
                flash('✓ Tabela e coluna já existem. Nada a fazer.', 'info')
            else:
                # Adicionar coluna modalidade
                if is_postgresql:
                    db.session.execute(text("""
                        ALTER TABLE horarios_professor 
                        ADD COLUMN modalidade VARCHAR(50) DEFAULT 'dublagem_presencial' NOT NULL
                    """))
                else:
                    db.session.execute(text("""
                        ALTER TABLE horarios_professor 
                        ADD COLUMN modalidade VARCHAR(50) DEFAULT 'dublagem_presencial' NOT NULL
                    """))
                
                # Atualizar horários existentes
                if is_postgresql:
                    db.session.execute(text("""
                        UPDATE horarios_professor 
                        SET modalidade = CASE
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.dublagem_presencial = true
                            ) THEN 'dublagem_presencial'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.dublagem_online = true
                            ) THEN 'dublagem_online'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.teatro_presencial = true
                            ) THEN 'teatro_presencial'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.teatro_online = true
                            ) THEN 'teatro_online'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.locucao = true
                            ) THEN 'locucao'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.musical = true
                            ) THEN 'musical'
                            ELSE 'dublagem_presencial'
                        END
                    """))
                else:
                    db.session.execute(text("""
                        UPDATE horarios_professor 
                        SET modalidade = CASE
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.dublagem_presencial = 1
                            ) THEN 'dublagem_presencial'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.dublagem_online = 1
                            ) THEN 'dublagem_online'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.teatro_presencial = 1
                            ) THEN 'teatro_presencial'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.teatro_online = 1
                            ) THEN 'teatro_online'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.locucao = 1
                            ) THEN 'locucao'
                            WHEN EXISTS (
                                SELECT 1 FROM professores p 
                                WHERE p.id = horarios_professor.professor_id 
                                AND p.musical = 1
                            ) THEN 'musical'
                            ELSE 'dublagem_presencial'
                        END
                    """))
                
                db.session.commit()
                flash('✓ Coluna modalidade adicionada com sucesso!', 'success')
        else:
            # Criar a tabela completa
            if is_postgresql:
                db.session.execute(text("""
                    CREATE TABLE horarios_professor (
                        id SERIAL PRIMARY KEY,
                        professor_id INTEGER NOT NULL,
                        dia_semana VARCHAR(20) NOT NULL,
                        horario_aula VARCHAR(50) NOT NULL,
                        modalidade VARCHAR(50) NOT NULL DEFAULT 'dublagem_presencial',
                        idade_minima INTEGER,
                        idade_maxima INTEGER,
                        CONSTRAINT fk_professor FOREIGN KEY (professor_id) 
                            REFERENCES professores(id) ON DELETE CASCADE
                    )
                """))
            else:
                db.session.execute(text("""
                    CREATE TABLE horarios_professor (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        professor_id INTEGER NOT NULL,
                        dia_semana VARCHAR(20) NOT NULL,
                        horario_aula VARCHAR(50) NOT NULL,
                        modalidade VARCHAR(50) NOT NULL DEFAULT 'dublagem_presencial',
                        idade_minima INTEGER,
                        idade_maxima INTEGER,
                        FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE
                    )
                """))
            
            db.session.commit()
            flash('✓ Tabela horarios_professor criada com sucesso!', 'success')
            
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = f"Erro na migração: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        flash(f'Erro na migração: {str(e)}', 'error')
    
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
@login_required
def api_professores():
    """API para buscar professores baseado nas modalidades selecionadas"""
    try:
        tipo_curso = request.args.get('tipo_curso', '').strip()
        
        if not tipo_curso:
            return jsonify([])
        
        # Filtrar apenas professores ativos
        query = Professor.query.filter_by(ativo=True)
        
        # Filtrar professores baseado no tipo de curso
        # Usar == True para compatibilidade com SQLite e PostgreSQL
        from sqlalchemy import or_
        
        if tipo_curso == 'dublagem_online':
            query = query.filter(Professor.dublagem_online == True)
        elif tipo_curso == 'dublagem_presencial':
            query = query.filter(Professor.dublagem_presencial == True)
        elif tipo_curso == 'teatro_online':
            query = query.filter(Professor.teatro_online == True)
        elif tipo_curso == 'teatro_presencial':
            query = query.filter(Professor.teatro_presencial == True)
        elif tipo_curso == 'locucao':
            query = query.filter(Professor.locucao == True)
        elif tipo_curso == 'musical':
            query = query.filter(Professor.musical == True)
        elif tipo_curso == 'teatro_tv_cinema':
            # Teatro TV/Cinema pode ser com professor de teatro presencial ou online
            query = query.filter(or_(Professor.teatro_presencial == True, Professor.teatro_online == True))
        else:
            # Se nenhum tipo foi especificado, retornar vazio
            return jsonify([])
        
        professores = query.order_by(Professor.nome).all()
        
        resultado = [{
            'id': p.id,
            'nome': p.nome,
            'dublagem_presencial': bool(p.dublagem_presencial),
            'dublagem_online': bool(p.dublagem_online),
            'teatro_presencial': bool(p.teatro_presencial),
            'teatro_online': bool(p.teatro_online),
            'musical': bool(p.musical),
            'locucao': bool(p.locucao),
            'curso_apresentador': bool(p.curso_apresentador)
        } for p in professores]
        
        return jsonify(resultado)
    except Exception as e:
        import traceback
        print(f"Erro na API de professores: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@bp.route('/api/professor/<int:professor_id>/horarios', methods=['GET'])
@login_required
def api_horarios_professor(professor_id):
    """API para buscar horários de um professor específico"""
    try:
        professor = Professor.query.get_or_404(professor_id)
        
        horarios = []
        for horario in professor.horarios:
            horarios.append({
                'id': horario.id,
                'dia_semana': horario.dia_semana,
                'horario_aula': horario.horario_aula
            })
        
        return jsonify(horarios)
    except Exception as e:
        import traceback
        print(f"Erro na API de horários: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

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
        elif filtro == 'pagamentos':
            # Para a aba de pagamentos, mostrar todos os alunos ativos
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas), subqueryload(Aluno.pagamentos)).filter_by(ativo=True).order_by(Aluno.nome).all()
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
        
        # Professores não podem ver alunos inativos - redirecionar para ativos
        if filtro == 'inativos':
            flash('Acesso negado. Apenas administradores podem visualizar alunos inativos.', 'error')
            return redirect(url_for('main.listar_alunos', filtro='ativos'))
        
        # Buscar alunos através de matrículas - carregar todas as matrículas do aluno, não apenas as do professor
        if filtro == 'pagamentos':
            # Para a aba de pagamentos, mostrar alunos ativos do professor
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas), subqueryload(Aluno.pagamentos)).join(Matricula).filter(
                Matricula.professor_id == professor.id,
                Aluno.ativo == True
            ).order_by(Aluno.nome).distinct().all()
        elif filtro == 'notas':
            # Para a aba de notas, filtrar por tipo_curso se fornecido
            tipo_curso = request.args.get('tipo_curso', '').strip()
            if tipo_curso:
                try:
                    # Filtrar alunos apenas do curso selecionado
                    alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).join(Matricula).filter(
                        Matricula.professor_id == professor.id,
                        Matricula.tipo_curso == tipo_curso,
                        Aluno.ativo == True
                    ).order_by(Aluno.nome).distinct().all()
                except Exception as e:
                    import traceback
                    print(f"Erro ao buscar alunos para notas: {e}")
                    print(traceback.format_exc())
                    alunos = []
                    flash(f'Erro ao buscar alunos: {str(e)}', 'error')
            else:
                # Se não há tipo_curso, não mostrar alunos
                alunos = []
                tipo_curso = None
        else:
            alunos = Aluno.query.options(subqueryload(Aluno.matriculas)).join(Matricula).filter(
                Matricula.professor_id == professor.id,
                Aluno.ativo == True
            ).order_by(Aluno.nome).distinct().all()
    else:
        # Aluno não pode ver lista
        flash('Acesso negado. Apenas administradores e professores podem ver a lista de alunos.', 'error')
        return redirect(url_for('main.index'))
    
    # Variáveis adicionais para a aba de notas
    # Nota: tipo_curso já foi definido acima quando filtro == 'notas' e é professor
    if filtro == 'notas':
        if not current_user.is_professor():
            # Para admin, buscar tipo_curso da URL
            tipo_curso = request.args.get('tipo_curso', '').strip() or None
        # Se for professor, tipo_curso já foi definido acima (linha 1195)
    else:
        tipo_curso = None
    
    numero_prova = request.args.get('numero_prova', type=int) if filtro == 'notas' else None
    data_prova_str = request.args.get('data_prova', '').strip() if filtro == 'notas' else None
    
    # Processar data_prova de forma segura
    data_prova = None
    if data_prova_str:
        try:
            data_prova = datetime.strptime(data_prova_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            data_prova = None
    
    # Se for professor e filtro for notas, buscar notas dos alunos
    notas_dict = {}
    if filtro == 'notas' and current_user.is_professor() and tipo_curso and alunos:
        from app.models.nota import Nota
        professor = current_user.get_professor()
        if professor:
            # Buscar TODAS as notas dos alunos para este curso (não apenas da prova atual)
            # Isso é necessário para calcular a média total de todas as provas
            try:
                alunos_ids = [aluno.id for aluno in alunos]
                if alunos_ids:
                    # Buscar todas as notas dos alunos para este curso e professor
                    notas = Nota.query.filter(
                        Nota.aluno_id.in_(alunos_ids),
                        Nota.professor_id == professor.id,
                        Nota.tipo_curso == tipo_curso
                    ).all()
                    
                    # Organizar notas por aluno e número da prova
                    for nota in notas:
                        try:
                            if nota and hasattr(nota, 'aluno_id') and hasattr(nota, 'numero_prova'):
                                if nota.aluno_id and nota.numero_prova:
                                    if nota.aluno_id not in notas_dict:
                                        notas_dict[nota.aluno_id] = {}
                                    notas_dict[nota.aluno_id][nota.numero_prova] = nota
                        except Exception as e:
                            # Continuar processando outras notas mesmo se uma falhar
                            print(f"Erro ao processar nota {nota.id if nota else 'None'}: {e}")
                            continue
            except Exception as e:
                # Em caso de erro, continuar com notas_dict vazio
                import traceback
                print(f"Erro ao buscar notas: {e}")
                print(traceback.format_exc())
                notas_dict = {}
    
    try:
        return render_template('listar_alunos.html', 
                             alunos=alunos, 
                             filtro=filtro, 
                             tipo_curso=tipo_curso,
                             numero_prova=numero_prova or 1,
                             data_prova=data_prova,
                             notas_dict=notas_dict,
                             motivos_exclusao=MOTIVOS_EXCLUSAO, 
                             data_hoje=date.today())
    except Exception as e:
        import traceback
        error_msg = f"Erro ao renderizar template: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        flash(f'Erro ao carregar página: {str(e)}', 'error')
        # Retornar uma versão simplificada sem notas
        return render_template('listar_alunos.html', 
                             alunos=alunos if alunos else [], 
                             filtro=filtro, 
                             tipo_curso=tipo_curso,
                             numero_prova=1,
                             data_prova=None,
                             notas_dict={},
                             motivos_exclusao=MOTIVOS_EXCLUSAO, 
                             data_hoje=date.today())

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

def obter_modalidades_professor(professor):
    """Função auxiliar para obter modalidades de um professor"""
    from sqlalchemy.orm import joinedload
    
    modalidades_professor = []
    professor_com_horarios = Professor.query.options(joinedload(Professor.horarios)).filter_by(id=professor.id).first()
    
    if professor_com_horarios and professor_com_horarios.horarios:
        modalidades_unicas = set()
        for horario in professor_com_horarios.horarios:
            try:
                if horario.modalidade:
                    modalidades_unicas.add(horario.modalidade)
            except AttributeError:
                pass
        
        # Se não encontrou modalidades nos horários, usar as modalidades do professor
        if not modalidades_unicas:
            if professor_com_horarios.dublagem_presencial:
                modalidades_unicas.add('dublagem_presencial')
            if professor_com_horarios.dublagem_online:
                modalidades_unicas.add('dublagem_online')
            if professor_com_horarios.teatro_presencial:
                modalidades_unicas.add('teatro_presencial')
            if professor_com_horarios.teatro_online:
                modalidades_unicas.add('teatro_online')
            if professor_com_horarios.locucao:
                modalidades_unicas.add('locucao')
            if professor_com_horarios.musical:
                modalidades_unicas.add('musical')
            if professor_com_horarios.teatro_tv_cinema:
                modalidades_unicas.add('teatro_tv_cinema')
            if professor_com_horarios.curso_apresentador:
                modalidades_unicas.add('curso_apresentador')
        
        tipos_cursos_map = {
            'dublagem_online': 'Dublagem Online',
            'dublagem_presencial': 'Dublagem Presencial',
            'teatro_presencial': 'Teatro Presencial',
            'teatro_online': 'Teatro Online',
            'locucao': 'Locução',
            'teatro_tv_cinema': 'Teatro TV e Cinema',
            'musical': 'Musical',
            'curso_apresentador': 'Curso de Apresentador'
        }
        
        modalidades_professor = [
            {'value': mod, 'label': tipos_cursos_map.get(mod, mod.replace('_', ' ').title())}
            for mod in sorted(modalidades_unicas)
        ]
    
    return modalidades_professor

@bp.route('/notas', methods=['GET'])
@login_required
def listar_notas():
    """Lista todas as notas (admin vê todas, professor vê apenas dos seus alunos)"""
    from sqlalchemy.orm import joinedload
    
    # Filtros
    aluno_id = request.args.get('aluno_id', type=int)
    tipo_curso = request.args.get('tipo_curso', '')
    
    # Base query com eager loading
    query = Nota.query.options(
        joinedload(Nota.aluno),
        joinedload(Nota.professor),
        joinedload(Nota.matricula)
    )
    
    # Variável para armazenar alunos (será usada tanto para professores quanto admins)
    alunos = []
    
    # Se for professor, só pode ver notas dos seus alunos
    if current_user.is_professor():
        professor = current_user.get_professor()
        if not professor:
            flash('Professor não encontrado.', 'error')
            return redirect(url_for('main.index'))
        
        # Para professor, tipo_curso é obrigatório
        if not tipo_curso:
            modalidades_professor = obter_modalidades_professor(professor)
            
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
                                 notas=[], 
                                 alunos=alunos, 
                                 aluno_id=None,
                                 tipo_curso='',
                                 modalidades_professor=modalidades_professor)
        
        # Buscar IDs dos alunos deste professor através das matrículas
        alunos_ids_query = db.session.query(Matricula.aluno_id).filter_by(
            professor_id=professor.id,
            tipo_curso=tipo_curso
        ).distinct()
        alunos_ids = [row[0] for row in alunos_ids_query.all()]
        
        if not alunos_ids:
            # Professor sem alunos nesta modalidade
            modalidades_professor = obter_modalidades_professor(professor)
            alunos = []
            return render_template('listar_notas.html', 
                                 notas=[], 
                                 alunos=alunos, 
                                 aluno_id=None,
                                 tipo_curso=tipo_curso,
                                 modalidades_professor=modalidades_professor)
        
        # Buscar os alunos completos para exibir na lista
        alunos = Aluno.query.filter(
            Aluno.id.in_(alunos_ids),
            Aluno.ativo == True
        ).order_by(Aluno.nome).all()
        
        query = query.filter(Nota.aluno_id.in_(alunos_ids))
        query = query.filter(Nota.professor_id == professor.id)
        query = query.filter(Nota.tipo_curso == tipo_curso)  # Já aplicar filtro de curso aqui
    
    # Aplicar filtros adicionais (apenas para admin)
    if aluno_id:
        query = query.filter(Nota.aluno_id == aluno_id)
    if tipo_curso and current_user.is_admin():
        query = query.filter(Nota.tipo_curso == tipo_curso)
    
    notas = query.order_by(Nota.data_avaliacao.desc(), Nota.data_cadastro.desc()).all()
    
    # Buscar alunos para filtros e exibição
    modalidades_professor = []
    
    if current_user.is_admin():
        alunos = Aluno.query.filter_by(ativo=True).order_by(Aluno.nome).all()
    elif current_user.is_professor():
        # Professor só vê seus próprios alunos
        professor = current_user.get_professor()
        if professor:
            modalidades_professor = obter_modalidades_professor(professor)
            
            # Se tipo_curso foi selecionado, os alunos já foram buscados acima (linhas 1675-1679)
            # Se não, buscar todos os alunos do professor (sem filtro de curso)
            if not tipo_curso:
                # Buscar todos os alunos do professor (sem filtro de curso)
                query_matriculas = db.session.query(Matricula.aluno_id).filter_by(
                    professor_id=professor.id
                )
                
                alunos_ids = query_matriculas.distinct().all()
                alunos_ids = [row[0] for row in alunos_ids]
                if alunos_ids:
                    alunos = Aluno.query.filter(
                        Aluno.id.in_(alunos_ids),
                        Aluno.ativo == True
                    ).order_by(Aluno.nome).all()
                else:
                    alunos = []
            # Se tipo_curso foi selecionado, a variável 'alunos' já foi definida acima (linhas 1675-1679)
            # e não precisa ser redefinida aqui
    
    return render_template('listar_notas.html', 
                         notas=notas, 
                         alunos=alunos, 
                         aluno_id=aluno_id,
                         tipo_curso=tipo_curso,
                         modalidades_professor=modalidades_professor)

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
    filtro_modalidade = request.args.get('filtro_modalidade', '').strip()
    
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
            query_matriculas = db.session.query(Matricula.aluno_id).filter_by(
                professor_id=professor.id
            )
            
            # Aplicar filtro de modalidade se fornecido
            if filtro_modalidade:
                query_matriculas = query_matriculas.filter_by(tipo_curso=filtro_modalidade)
            
            alunos_ids = query_matriculas.distinct().all()
            alunos_ids = [row[0] for row in alunos_ids]
            
            if alunos_ids:
                alunos = Aluno.query.filter(
                    Aluno.id.in_(alunos_ids),
                    Aluno.ativo == True
                ).order_by(Aluno.nome).all()
            
            professores = [professor]  # Professor só pode cadastrar para si mesmo
            
            if aluno_id:
                query_matriculas_aluno = Matricula.query.filter_by(
                    aluno_id=aluno_id,
                    professor_id=professor.id
                )
                if filtro_modalidade:
                    query_matriculas_aluno = query_matriculas_aluno.filter_by(tipo_curso=filtro_modalidade)
                matriculas = query_matriculas_aluno.all()
    
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
                         filtro_modalidade=filtro_modalidade,
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

@bp.route('/notas/salvar-criterios', methods=['POST'])
@login_required
def salvar_criterios_notas():
    """Salvar notas com critérios para múltiplos alunos de uma vez"""
    if not current_user.is_professor():
        flash('Acesso negado. Apenas professores podem salvar notas com critérios.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    professor = current_user.get_professor()
    if not professor:
        flash('Professor não encontrado.', 'error')
        return redirect(url_for('main.listar_alunos'))
    
    # Obter dados do formulário
    tipo_curso = request.form.get('tipo_curso', '').strip()
    numero_prova = request.form.get('numero_prova', type=int)
    data_avaliacao_str = request.form.get('data_avaliacao', '').strip()
    
    if not tipo_curso:
        flash('Tipo de curso é obrigatório.', 'error')
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso))
    
    if not numero_prova:
        flash('Número da prova é obrigatório.', 'error')
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso))
    
    if not data_avaliacao_str:
        flash('Data da avaliação é obrigatória.', 'error')
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso))
    
    try:
        data_avaliacao = datetime.strptime(data_avaliacao_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data da avaliação inválida.', 'error')
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso))
    
    # Processar notas de cada aluno
    notas_salvas = 0
    notas_atualizadas = 0
    erros = []
    
    try:
        # Buscar todos os campos do formulário que começam com "aluno_"
        alunos_processados = set()
        for key in request.form.keys():
            if key.startswith('aluno_') and key.endswith('_criterio1'):
                # Extrair ID do aluno do nome do campo (formato: aluno_{id}_criterio1)
                try:
                    aluno_id = int(key.split('_')[1])
                    alunos_processados.add(aluno_id)
                except (ValueError, IndexError):
                    continue
        
        for aluno_id in alunos_processados:
            try:
                # Buscar aluno
                aluno = Aluno.query.get(aluno_id)
                if not aluno:
                    erros.append(f'Aluno ID {aluno_id} não encontrado.')
                    continue
                
                # Verificar se o aluno está matriculado com este professor neste curso
                matricula = Matricula.query.filter_by(
                    aluno_id=aluno_id,
                    professor_id=professor.id,
                    tipo_curso=tipo_curso
                ).first()
                
                if not matricula:
                    erros.append(f'Aluno {aluno.nome} não está matriculado neste curso com este professor.')
                    continue
                
                # Obter valores dos critérios
                criterio1_str = request.form.get(f'aluno_{aluno_id}_criterio1', '').strip()
                criterio2_str = request.form.get(f'aluno_{aluno_id}_criterio2', '').strip()
                criterio3_str = request.form.get(f'aluno_{aluno_id}_criterio3', '').strip()
                criterio4_str = request.form.get(f'aluno_{aluno_id}_criterio4', '').strip()
                
                # Converter para float (None se vazio)
                criterio1 = float(criterio1_str) if criterio1_str else None
                criterio2 = float(criterio2_str) if criterio2_str else None
                criterio3 = float(criterio3_str) if criterio3_str else None
                criterio4 = float(criterio4_str) if criterio4_str else None
                
                # Validar que pelo menos um critério foi preenchido
                if criterio1 is None and criterio2 is None and criterio3 is None and criterio4 is None:
                    continue  # Pular se nenhum critério foi preenchido
                
                # Validar valores (0 a 10)
                for i, criterio in enumerate([criterio1, criterio2, criterio3, criterio4], 1):
                    if criterio is not None and (criterio < 0 or criterio > 10):
                        erros.append(f'Aluno {aluno.nome}: Critério {i} deve estar entre 0 e 10.')
                        continue
                
                # Calcular valor (média dos critérios preenchidos)
                criterios_preenchidos = [c for c in [criterio1, criterio2, criterio3, criterio4] if c is not None]
                valor = 0.0  # Valor padrão
                if criterios_preenchidos:
                    valor = sum(criterios_preenchidos) / len(criterios_preenchidos)
                
                # Verificar se já existe nota para este aluno, professor, curso e prova
                nota_existente = Nota.query.filter_by(
                    aluno_id=aluno_id,
                    professor_id=professor.id,
                    tipo_curso=tipo_curso,
                    numero_prova=numero_prova
                ).first()
                
                if nota_existente:
                    # Atualizar nota existente
                    nota_existente.criterio1 = criterio1
                    nota_existente.criterio2 = criterio2
                    nota_existente.criterio3 = criterio3
                    nota_existente.criterio4 = criterio4
                    nota_existente.valor = valor  # Atualizar valor calculado
                    nota_existente.data_avaliacao = data_avaliacao
                    nota_existente.matricula_id = matricula.id
                    notas_atualizadas += 1
                else:
                    # Criar nova nota
                    nota = Nota(
                        aluno_id=aluno_id,
                        professor_id=professor.id,
                        matricula_id=matricula.id,
                        tipo_curso=tipo_curso,
                        numero_prova=numero_prova,
                        criterio1=criterio1,
                        criterio2=criterio2,
                        criterio3=criterio3,
                        criterio4=criterio4,
                        valor=valor,  # Preencher valor calculado
                        data_avaliacao=data_avaliacao,
                        tipo_avaliacao=f'Prova {numero_prova}',
                        cadastrado_por=current_user.id
                    )
                    db.session.add(nota)
                    notas_salvas += 1
                    
            except Exception as e:
                erros.append(f'Erro ao processar aluno ID {aluno_id}: {str(e)}')
                continue
        
        # Commit de todas as alterações
        db.session.commit()
        
        # Mensagens de sucesso
        if notas_salvas > 0:
            flash(f'{notas_salvas} nota(s) cadastrada(s) com sucesso!', 'success')
        if notas_atualizadas > 0:
            flash(f'{notas_atualizadas} nota(s) atualizada(s) com sucesso!', 'success')
        if erros:
            for erro in erros:
                flash(erro, 'error')
        
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso, numero_prova=numero_prova, data_prova=data_avaliacao_str))
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Erro ao salvar critérios de notas: {e}")
        print(traceback.format_exc())
        flash(f'Erro ao salvar notas: {str(e)}', 'error')
        data_avaliacao_str = request.form.get('data_avaliacao', '').strip()
        return redirect(url_for('main.listar_alunos', filtro='notas', tipo_curso=tipo_curso, numero_prova=numero_prova, data_prova=data_avaliacao_str))

# ==================== ROTAS DE PAGAMENTO ====================

@bp.route('/alunos/<int:aluno_id>/pagamento/upload', methods=['GET', 'POST'])
@login_required
def upload_comprovante(aluno_id):
    """Upload de comprovante de pagamento"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Verificar permissão: apenas administradores podem enviar comprovantes
    if not current_user.is_admin():
        flash('Acesso negado. Apenas administradores podem enviar comprovantes.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Validar credenciais do Cloudinary
            import cloudinary
            import cloudinary.uploader
            
            cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
            api_key = current_app.config.get('CLOUDINARY_API_KEY')
            api_secret = current_app.config.get('CLOUDINARY_API_SECRET')
            
            if not api_key or not api_secret:
                flash('Erro de configuração: Credenciais do Cloudinary não encontradas. Entre em contato com o administrador.', 'error')
                return render_template('upload_comprovante.html', aluno=aluno)
            
            # Obter dados do formulário
            mes_referencia = request.form.get('mes_referencia', '').strip()
            ano_referencia = request.form.get('ano_referencia', '').strip()
            valor_pago = request.form.get('valor_pago', '').strip()
            data_pagamento_str = request.form.get('data_pagamento', '').strip()
            observacoes = request.form.get('observacoes', '').strip()
    
            # Validações
            erros = []
            
            if not mes_referencia:
                erros.append('Mês de referência é obrigatório.')
            else:
                try:
                    mes_referencia = int(mes_referencia)
                    if mes_referencia < 1 or mes_referencia > 12:
                        erros.append('Mês inválido.')
                except ValueError:
                    erros.append('Mês inválido.')
            
            if not ano_referencia:
                erros.append('Ano de referência é obrigatório.')
            else:
                try:
                    ano_referencia = int(ano_referencia)
                    if ano_referencia < 2020 or ano_referencia > 2100:
                        erros.append('Ano inválido.')
                except ValueError:
                    erros.append('Ano inválido.')
            
            if not valor_pago:
                erros.append('Valor pago é obrigatório.')
            else:
                try:
                    valor_pago = float(valor_pago.replace(',', '.'))
                    if valor_pago <= 0:
                        erros.append('Valor pago deve ser maior que zero.')
                except ValueError:
                    erros.append('Valor pago inválido.')
            
            if not data_pagamento_str:
                erros.append('Data do pagamento é obrigatória.')
            else:
                try:
                    data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()
                except ValueError:
                    erros.append('Data do pagamento inválida.')
            
            # Validar arquivo
            if 'comprovante' not in request.files:
                erros.append('Comprovante é obrigatório.')
            else:
                arquivo = request.files['comprovante']
                if arquivo.filename == '':
                    erros.append('Comprovante é obrigatório.')
                else:
                    # Validar extensão
                    extensoes_permitidas = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.webp'}
                    nome_arquivo = secure_filename(arquivo.filename)
                    _, ext = os.path.splitext(nome_arquivo.lower())
                    
                    if ext not in extensoes_permitidas:
                        erros.append(f'Formato de arquivo não permitido. Use: {", ".join(extensoes_permitidas)}')
                    
                    # Validar tamanho (10MB)
                    arquivo.seek(0, os.SEEK_END)
                    tamanho = arquivo.tell()
                    arquivo.seek(0)
                    if tamanho > 10 * 1024 * 1024:  # 10MB
                        erros.append('Arquivo muito grande. Tamanho máximo: 10MB')
            
            if erros:
                for erro in erros:
                    flash(erro, 'error')
                return render_template('upload_comprovante.html', aluno=aluno)
            
            # Verificar se já existe pagamento aprovado para o mesmo mês/ano
            pagamento_existente = Pagamento.query.filter_by(
                aluno_id=aluno_id,
                mes_referencia=mes_referencia,
                ano_referencia=ano_referencia,
                status='aprovado'
            ).first()
            
            if pagamento_existente:
                flash(f'Já existe um pagamento aprovado para {mes_referencia}/{ano_referencia}.', 'error')
                return render_template('upload_comprovante.html', aluno=aluno)
            
            # Fazer upload para Cloudinary
            try:
                arquivo.seek(0)  # Garantir que está no início
                resultado = cloudinary.uploader.upload(
                    arquivo,
                    folder=f'comprovantes/{aluno_id}',
                    resource_type='auto',
                    allowed_formats=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'webp']
                )
                
                url_comprovante = resultado.get('secure_url')
                public_id = resultado.get('public_id')
                
            except Exception as e:
                flash(f'Erro ao fazer upload do comprovante: {str(e)}', 'error')
                return render_template('upload_comprovante.html', aluno=aluno)
            
            # Criar registro de pagamento
            pagamento = Pagamento(
                    aluno_id=aluno_id,
                mes_referencia=mes_referencia,
                ano_referencia=ano_referencia,
                valor_pago=valor_pago,
                data_pagamento=data_pagamento,
                url_comprovante=url_comprovante,
                public_id=public_id,
                observacoes=observacoes if observacoes else None,
                status='pendente'
            )
            
            db.session.add(pagamento)
            db.session.commit()
            
            flash('Comprovante enviado com sucesso! Aguardando aprovação do administrador.', 'success')
            return redirect(url_for('main.listar_pagamentos_aluno', aluno_id=aluno_id))
            
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"Erro ao processar upload: {traceback.format_exc()}")
            flash(f'Erro ao processar upload: {str(e)}', 'error')
            return render_template('upload_comprovante.html', aluno=aluno)
    
    # GET - mostrar formulário
    return render_template('upload_comprovante.html', aluno=aluno)

@bp.route('/alunos/<int:aluno_id>/pagamentos')
@login_required
def listar_pagamentos_aluno(aluno_id):
    """Listar pagamentos de um aluno específico"""
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Verificar permissão: admin ou professor podem acessar qualquer aluno
    if not current_user.is_admin() and not current_user.is_professor():
        flash('Acesso negado. Apenas administradores e professores podem visualizar pagamentos.', 'error')
        return redirect(url_for('main.index'))
    
    pagamentos = Pagamento.query.filter_by(aluno_id=aluno_id).order_by(
        Pagamento.ano_referencia.desc(),
        Pagamento.mes_referencia.desc()
    ).all()
    
    return render_template('listar_pagamentos_aluno.html', aluno=aluno, pagamentos=pagamentos)

@bp.route('/pagamentos')
@admin_required
def listar_pagamentos():
    """Listar todos os pagamentos (apenas admin)"""
    # Filtros
    status_filtro = request.args.get('status', '').strip()
    aluno_id_filtro = request.args.get('aluno_id', '').strip()
    mes_filtro = request.args.get('mes', '').strip()
    ano_filtro = request.args.get('ano', '').strip()
    
    # Query base - buscar TODOS os pagamentos
    query = Pagamento.query
    
    # Aplicar filtros apenas se tiverem valor válido (não vazio)
    # Status: aplicar apenas se não for vazio
    if status_filtro and status_filtro.strip():
        query = query.filter_by(status=status_filtro)
    
    # Aluno: aplicar apenas se não for vazio
    if aluno_id_filtro and aluno_id_filtro.strip():
        try:
            query = query.filter_by(aluno_id=int(aluno_id_filtro))
        except (ValueError, TypeError):
            pass
    
    # Mês: aplicar apenas se não for vazio
    if mes_filtro and mes_filtro.strip():
        try:
            query = query.filter_by(mes_referencia=int(mes_filtro))
        except (ValueError, TypeError):
            pass
    
    # Ano: aplicar apenas se não for vazio
    if ano_filtro and ano_filtro.strip():
        try:
            query = query.filter_by(ano_referencia=int(ano_filtro))
        except (ValueError, TypeError):
            pass
    
    pagamentos = query.order_by(
        Pagamento.data_cadastro.desc()
    ).all()
    
    # Buscar alunos para o filtro
    alunos = Aluno.query.filter_by(ativo=True).order_by(Aluno.nome).all()
    
    return render_template('listar_pagamentos.html', 
                         pagamentos=pagamentos,
                         alunos=alunos,
                         status_filtro=status_filtro,
                         aluno_id_filtro=aluno_id_filtro,
                         mes_filtro=mes_filtro,
                         ano_filtro=ano_filtro)

@bp.route('/pagamentos/<int:pagamento_id>/aprovar', methods=['POST'])
@admin_required
def aprovar_pagamento(pagamento_id):
    """Aprovar um pagamento"""
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    
    if pagamento.status != 'pendente':
        flash('Este pagamento já foi processado.', 'info')
        return redirect(url_for('main.listar_pagamentos'))
    
    observacoes_admin = request.form.get('observacoes_admin', '').strip()
    
    pagamento.status = 'aprovado'
    pagamento.aprovado_por = current_user.id
    pagamento.data_aprovacao = datetime.now()
    if observacoes_admin:
        pagamento.observacoes_admin = observacoes_admin
    
    # Atualizar data de vencimento do aluno se o pagamento for do mês corrente
    aluno = pagamento.aluno
    if aluno:
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Verificar se o pagamento é do mês corrente
        if pagamento.mes_referencia == mes_atual and pagamento.ano_referencia == ano_atual:
            # Calcular próxima data de vencimento (próximo mês, mantendo o dia)
            if mes_atual == 12:
                # Se for dezembro, vai para janeiro do próximo ano
                proximo_mes = 1
                proximo_ano = ano_atual + 1
            else:
                proximo_mes = mes_atual + 1
                proximo_ano = ano_atual
            
            # Manter o dia da data de vencimento atual
            dia_vencimento = aluno.data_vencimento.day if aluno.data_vencimento else hoje.day
            
            # Ajustar o dia se o próximo mês não tiver esse dia (ex: 31 de janeiro -> 28/29 de fevereiro)
            try:
                nova_data_vencimento = date(proximo_ano, proximo_mes, dia_vencimento)
            except ValueError:
                # Se o dia não existe no próximo mês (ex: 31 de janeiro -> fevereiro), usar o último dia do mês
                from calendar import monthrange
                ultimo_dia = monthrange(proximo_ano, proximo_mes)[1]
                nova_data_vencimento = date(proximo_ano, proximo_mes, ultimo_dia)
            
            aluno.data_vencimento = nova_data_vencimento
            # Atualizar também o campo legado dia_vencimento
            aluno.dia_vencimento = nova_data_vencimento.day
    
    try:
        db.session.commit()
        flash(f'Pagamento de {pagamento.aluno.nome if pagamento.aluno else "aluno"} aprovado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar pagamento: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_pagamentos'))

@bp.route('/pagamentos/<int:pagamento_id>/rejeitar', methods=['POST'])
@admin_required
def rejeitar_pagamento(pagamento_id):
    """Rejeitar um pagamento"""
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    
    if pagamento.status != 'pendente':
        flash('Este pagamento já foi processado.', 'info')
        return redirect(url_for('main.listar_pagamentos'))
    
    observacoes_admin = request.form.get('observacoes_admin', '').strip()
    
    if not observacoes_admin:
        flash('É obrigatório informar o motivo da rejeição.', 'error')
        return redirect(url_for('main.listar_pagamentos'))
    
    pagamento.status = 'rejeitado'
    pagamento.aprovado_por = current_user.id
    pagamento.data_aprovacao = datetime.now()
    pagamento.observacoes_admin = observacoes_admin
    
    try:
        db.session.commit()
        flash(f'Pagamento de {pagamento.aluno.nome if pagamento.aluno else "aluno"} rejeitado.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao rejeitar pagamento: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_pagamentos'))

@bp.route('/pagamentos/<int:pagamento_id>/deletar', methods=['POST'])
@admin_required
def deletar_pagamento(pagamento_id):
    """Deletar um pagamento e seu comprovante"""
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    
    # Deletar arquivo do Cloudinary se existir
    if pagamento.public_id:
        try:
            import cloudinary.uploader
            cloudinary.uploader.destroy(pagamento.public_id)
        except Exception as e:
            print(f"Erro ao deletar arquivo do Cloudinary: {e}")
            # Continuar mesmo se houver erro ao deletar o arquivo
    
    try:
        db.session.delete(pagamento)
        db.session.commit()
        flash('Pagamento deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar pagamento: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_pagamentos'))

# ==================== ROTAS DE NOTIFICAÇÕES WHATSAPP ====================

@bp.route('/notificacoes/enviar-vencimentos', methods=['POST'])
@admin_required
def enviar_notificacoes_vencimentos():
    """Envia notificações WhatsApp para alunos com vencimento hoje"""
    import logging
    logger = logging.getLogger(__name__)
    
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        # Verificar se WhatsApp está habilitado
        if not current_app.config.get('WHATSAPP_ENABLED', False):
            flash('WhatsApp não está habilitado. Configure as variáveis de ambiente.', 'error')
            return redirect(url_for('main.listar_alunos'))
        
        # Inicializar serviço WhatsApp
        whatsapp = WhatsAppService(
            account_sid=current_app.config.get('TWILIO_ACCOUNT_SID'),
            auth_token=current_app.config.get('TWILIO_AUTH_TOKEN'),
            from_number=current_app.config.get('TWILIO_WHATSAPP_FROM')
        )
        
        # Enviar notificações
        resultados = whatsapp.notificar_vencimentos_hoje()
        
        # Exibir resultados
        if resultados['enviadas'] > 0:
            flash(f'✅ {resultados["enviadas"]} notificação(ões) enviada(s) com sucesso!', 'success')
        
        if resultados['erros'] > 0:
            flash(f'⚠️ {resultados["erros"]} erro(s) ao enviar notificação(ões).', 'error')
        
        if resultados['enviadas'] == 0 and resultados['erros'] == 0:
            flash('Nenhum aluno com vencimento hoje encontrado.', 'info')
        
        # Log detalhado
        if resultados['detalhes']:
            for detalhe in resultados['detalhes']:
                if detalhe['status'] == 'erro':
                    logger.warning(f"Erro ao notificar {detalhe['aluno']}: {detalhe.get('mensagem', 'Erro desconhecido')}")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao enviar notificações: {e}")
        flash(f'Erro ao enviar notificações: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_alunos'))

@bp.route('/notificacoes/testar', methods=['GET', 'POST'])
@admin_required
def testar_notificacao_whatsapp():
    """Página para testar envio de notificação WhatsApp"""
    import traceback
    
    try:
        from app.services.whatsapp_service import WhatsAppService
    except ImportError as e:
        flash(f'Erro ao importar serviço WhatsApp: {str(e)}. Verifique se o twilio está instalado (pip install twilio).', 'error')
        import traceback
        traceback.print_exc()
        # Preparar informações básicas para o template mesmo com erro
        config_info = {
            'whatsapp_from': 'Erro na configuração',
            'whatsapp_enabled': False
        }
        return render_template('testar_notificacao.html', config_info=config_info)
    
    # Preparar informações para o template
    config_info = {
        'whatsapp_from': current_app.config.get('TWILIO_WHATSAPP_FROM', 'Não configurado'),
        'whatsapp_enabled': current_app.config.get('WHATSAPP_ENABLED', False)
    }
    
    if request.method == 'POST':
        telefone = request.form.get('telefone', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        
        if not telefone or not mensagem:
            flash('Telefone e mensagem são obrigatórios.', 'error')
            return render_template('testar_notificacao.html', config_info=config_info)
        
        try:
            whatsapp = WhatsAppService(
                account_sid=current_app.config.get('TWILIO_ACCOUNT_SID'),
                auth_token=current_app.config.get('TWILIO_AUTH_TOKEN'),
                from_number=current_app.config.get('TWILIO_WHATSAPP_FROM')
            )
            
            sucesso, resultado = whatsapp.enviar_mensagem(telefone, mensagem)
            
            if sucesso:
                status_info = f", Status: {resultado.get('status', 'N/A')}" if isinstance(resultado, dict) else ""
                flash(f'✅ Mensagem enviada! ID: {resultado.get("sid", resultado) if isinstance(resultado, dict) else resultado}{status_info}', 'success')
            else:
                if isinstance(resultado, dict):
                    erro_msg = resultado.get('erro', 'Erro desconhecido')
                    status_info = f" (Status: {resultado.get('status', 'N/A')})" if resultado.get('status') else ""
                    flash(f'❌ Erro: {erro_msg}{status_info}', 'error')
                else:
                    flash(f'❌ Erro ao enviar mensagem: {resultado}', 'error')
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            flash(f'Erro: {str(e)}', 'error')
            # Log do erro completo para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao enviar mensagem de teste: {error_trace}")
    
    return render_template('testar_notificacao.html', config_info=config_info)


