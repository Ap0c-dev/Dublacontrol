from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.professor import db, Professor
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from datetime import datetime, date

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('main.cadastro_professores'))

@bp.route('/cadastro-professores', methods=['GET', 'POST'])
def cadastro_professores():
    if request.method == 'POST':
        professores_data = request.form.getlist('professores[]')
        
        if not professores_data:
            flash('Nenhum professor foi enviado.', 'error')
            return render_template('cadastro_professores.html')
        
        professores_cadastrados = 0
        erros = []
        
        # Processar cada professor do formulário
        for i, professor_data in enumerate(professores_data):
            # Obter dados do professor
            nome = request.form.get(f'nome_{i}', '').strip()
            telefone = request.form.get(f'telefone_{i}', '').strip()
            
            # Validação: telefone obrigatório e formato
            if not telefone:
                erros.append(f'Professor {i+1}: Telefone é obrigatório.')
                continue
            
            # Validar formato do telefone (apenas números, DDD + 9 dígitos = 11 dígitos)
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if len(telefone_limpo) != 11:
                erros.append(f'Professor {i+1}: Telefone inválido. Deve conter DDD + 9 dígitos (11 números).')
                continue
            
            telefone = telefone_limpo
            
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
            
            # Criar e salvar professor
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
                    curso_apresentador=curso_apresentador
                )
                db.session.add(professor)
                professores_cadastrados += 1
            except Exception as e:
                erros.append(f'Professor {i+1} ({nome}): Erro ao cadastrar - {str(e)}')
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
        
        if professores_cadastrados > 0:
            try:
                db.session.commit()
                flash(f'{professores_cadastrados} professor(es) cadastrado(s) com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao salvar no banco de dados: {str(e)}', 'error')
        
        return redirect(url_for('main.cadastro_professores'))
    
    return render_template('cadastro_professores.html')

@bp.route('/professores')
def listar_professores():
    professores = Professor.query.order_by(Professor.nome).all()
    return render_template('listar_professores.html', professores=professores)

@bp.route('/api/professores', methods=['GET'])
def api_professores():
    """API para buscar professores baseado nas modalidades selecionadas"""
    tipo_curso = request.args.get('tipo_curso', '').strip()
    
    query = Professor.query
    
    # Filtrar professores baseado no tipo de curso
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
    
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'dublagem_presencial': p.dublagem_presencial,
        'dublagem_online': p.dublagem_online,
        'teatro_presencial': p.teatro_presencial,
        'teatro_online': p.teatro_online,
        'musical': p.musical,
        'locucao': p.locucao,
        'curso_apresentador': p.curso_apresentador
    } for p in professores])

@bp.route('/cadastro-alunos', methods=['GET', 'POST'])
def cadastro_alunos():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        nome_responsavel = request.form.get('nome_responsavel', '').strip()
        telefone_responsavel = request.form.get('telefone_responsavel', '').strip()
        data_nascimento_str = request.form.get('data_nascimento', '').strip()
        
        # Endereço - campos separados
        rua = request.form.get('rua', '').strip()
        numero = request.form.get('numero', '').strip()
        bairro = request.form.get('bairro', '').strip()
        cidade = request.form.get('cidade', '').strip()
        pais = request.form.get('pais', '').strip()
        
        # Cursos e professores associados
        cursos_professores = {}
        tipos_cursos = ['dublagem_online', 'dublagem_presencial', 'teatro_online', 'teatro_presencial', 'locucao', 'teatro_tv_cinema', 'musical']
        
        dublagem_online = request.form.get('dublagem_online') == 'on'
        dublagem_presencial = request.form.get('dublagem_presencial') == 'on'
        teatro_online = request.form.get('teatro_online') == 'on'
        teatro_presencial = request.form.get('teatro_presencial') == 'on'
        locucao = request.form.get('locucao') == 'on'
        teatro_tv_cinema = request.form.get('teatro_tv_cinema') == 'on'
        musical = request.form.get('musical') == 'on'
        
        # Coletar professores para cada curso selecionado
        for tipo_curso in tipos_cursos:
            professor_id_str = request.form.get(f'professor_{tipo_curso}', '').strip()
            if professor_id_str:
                try:
                    professor_id = int(professor_id_str)
                    cursos_professores[tipo_curso] = professor_id
                except ValueError:
                    pass
        
        # Validação: nome obrigatório
        if not nome:
            flash('Nome do aluno é obrigatório.', 'error')
            return render_template('cadastro_alunos.html')
        
        # Validação: telefone obrigatório e formato
        if not telefone:
            flash('Telefone do aluno é obrigatório.', 'error')
            return render_template('cadastro_alunos.html')
        
        # Validar formato do telefone (apenas números, DDD + 9 dígitos = 11 dígitos)
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if len(telefone_limpo) != 11:
            flash('Telefone inválido. Deve conter DDD + 9 dígitos (ex: 11987654321).', 'error')
            return render_template('cadastro_alunos.html')
        
        telefone = telefone_limpo
        
        # Processar data de nascimento
        data_nascimento = None
        idade = None
        if data_nascimento_str:
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                # Calcular idade
                today = date.today()
                idade = today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))
                if idade < 0:
                    idade = 0
            except ValueError:
                flash('Data de nascimento inválida.', 'error')
                return render_template('cadastro_alunos.html')
        
        # Validação: responsável obrigatório para menores de 16 anos
        if idade is not None and idade < 16:
            if not nome_responsavel:
                flash('Nome do responsável é obrigatório para menores de 16 anos.', 'error')
                return render_template('cadastro_alunos.html')
            
            if not telefone_responsavel:
                flash('Telefone do responsável é obrigatório para menores de 16 anos.', 'error')
                return render_template('cadastro_alunos.html')
            
            # Validar formato do telefone do responsável
            telefone_responsavel_limpo = ''.join(filter(str.isdigit, telefone_responsavel))
            if len(telefone_responsavel_limpo) != 11:
                flash('Telefone do responsável inválido. Deve conter DDD + 9 dígitos.', 'error')
                return render_template('cadastro_alunos.html')
            
            telefone_responsavel = telefone_responsavel_limpo
        
        # Criar e salvar aluno
        try:
            aluno = Aluno(
                nome=nome,
                telefone=telefone,
                nome_responsavel=nome_responsavel if nome_responsavel else None,
                telefone_responsavel=telefone_responsavel if telefone_responsavel else None,
                data_nascimento=data_nascimento,
                idade=idade,
                rua=rua if rua else None,
                numero=numero if numero else None,
                bairro=bairro if bairro else None,
                cidade=cidade if cidade else None,
                pais=pais if pais else None,
                dublagem_online=dublagem_online,
                dublagem_presencial=dublagem_presencial,
                teatro_online=teatro_online,
                teatro_presencial=teatro_presencial,
                locucao=locucao,
                teatro_tv_cinema=teatro_tv_cinema,
                musical=musical
            )
            db.session.add(aluno)
            db.session.flush()  # Para obter o ID do aluno
            
            # Criar matrículas para cada curso com professor selecionado
            for tipo_curso, professor_id in cursos_professores.items():
                matricula = Matricula(
                    aluno_id=aluno.id,
                    professor_id=professor_id,
                    tipo_curso=tipo_curso
                )
                db.session.add(matricula)
            
            db.session.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
            return redirect(url_for('main.cadastro_alunos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar aluno: {str(e)}', 'error')
            return render_template('cadastro_alunos.html')
    
    return render_template('cadastro_alunos.html')

@bp.route('/alunos')
def listar_alunos():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template('listar_alunos.html', alunos=alunos)

