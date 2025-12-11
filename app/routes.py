from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.professor import db, Professor
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from datetime import datetime, date
import re

bp = Blueprint('main', __name__)

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
    return redirect(url_for('main.cadastro_professores'))

@bp.route('/cadastro-professores', methods=['GET', 'POST'])
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
                nome = request.form.get(f'nome_{i}', '').strip()
                telefone = request.form.get(f'telefone_{i}', '').strip()
                
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
                
                # Verificar se o professor já existe (mesmo nome e telefone)
                professor_existente = Professor.query.filter_by(
                    nome=nome,
                    telefone=telefone
                ).first()
                
                if professor_existente:
                    erros.append(f'Professor {i+1} ({nome}): Já existe um professor cadastrado com este nome e telefone.')
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
def listar_professores():
    professores = Professor.query.order_by(Professor.nome).all()
    return render_template('listar_professores.html', professores=professores)

@bp.route('/api/professores', methods=['GET'])
def api_professores():
    """API para buscar professores baseado nas modalidades selecionadas"""
    tipo_curso = request.args.get('tipo_curso', '').strip()
    
    if not tipo_curso:
        return jsonify([])
    
    query = Professor.query
    
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

@bp.route('/cadastro-alunos', methods=['GET', 'POST'])
def cadastro_alunos():
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
                nome = request.form.get(f'nome_{i}', '').strip()
                telefone = request.form.get(f'telefone_{i}', '').strip()
                nome_responsavel = request.form.get(f'nome_responsavel_{i}', '').strip()
                telefone_responsavel = request.form.get(f'telefone_responsavel_{i}', '').strip()
                data_nascimento_str = request.form.get(f'data_nascimento_{i}', '').strip()
                
                # Endereço - apenas cidade e estado (obrigatórios)
                cidade = request.form.get(f'cidade_{i}', '').strip()
                estado = request.form.get(f'estado_{i}', '').strip().upper()
                
                # Forma de pagamento e dia de vencimento
                forma_pagamento = request.form.get(f'forma_pagamento_{i}', '').strip()
                dia_vencimento_str = request.form.get(f'dia_vencimento_{i}', '').strip()
                
                # Validação: nome obrigatório
                if not nome:
                    erros.append(f'Aluno {i+1}: Nome é obrigatório.')
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
                
                # Processar data de nascimento
                data_nascimento = None
                idade = None
                if data_nascimento_str:
                    try:
                        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
                        today = date.today()
                        idade = today.year - data_nascimento.year - ((today.month, today.day) < (data_nascimento.month, data_nascimento.day))
                        if idade < 0:
                            idade = 0
                        
                        # Validar idade entre 5 e 100 anos
                        if idade < 5:
                            erros.append(f'Aluno {i+1} ({nome}): Idade Inválida')
                            continue
                        if idade > 100:
                            erros.append(f'Aluno {i+1} ({nome}): Idade Inválida')
                            continue
                    except ValueError:
                        erros.append(f'Aluno {i+1} ({nome}): Data de nascimento inválida.')
                        continue
                
                # Validação: forma de pagamento obrigatória
                if not forma_pagamento:
                    erros.append(f'Aluno {i+1} ({nome}): Forma de pagamento é obrigatória.')
                    continue
                
                # Validação: dia de vencimento obrigatório (1-31)
                if not dia_vencimento_str:
                    erros.append(f'Aluno {i+1} ({nome}): Dia de vencimento é obrigatório.')
                    continue
                
                try:
                    dia_vencimento = int(dia_vencimento_str)
                    if dia_vencimento < 1 or dia_vencimento > 31:
                        erros.append(f'Aluno {i+1} ({nome}): Dia de vencimento deve ser entre 1 e 31.')
                        continue
                except ValueError:
                    erros.append(f'Aluno {i+1} ({nome}): Dia de vencimento inválido.')
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
                
                # Verificar se o aluno já existe (mesmo nome e telefone)
                aluno_existente = Aluno.query.filter_by(
                    nome=nome,
                    telefone=telefone
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
                        
                        # Validação: se curso está selecionado, professor é obrigatório
                        if not professor_id_str:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): É obrigatório selecionar um professor para o curso "{nome_curso}".')
                            continue
                        
                        # Validação: se curso está selecionado, mensalidade é obrigatória
                        if not mensalidade_str:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): É obrigatório informar a mensalidade para o curso "{nome_curso}".')
                            continue
                        
                        try:
                            professor_id = int(professor_id_str)
                            
                            # Processar mensalidade (obrigatória e deve ser > 0)
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
                                'valor_mensalidade': valor_mensalidade
                            }
                        except ValueError:
                            nome_curso = tipo_curso.replace('_', ' ').title()
                            erros.append(f'Aluno {i+1} ({nome}): Professor inválido para o curso "{nome_curso}".')
                            continue
                
                # Criar aluno
                aluno = Aluno(
                    nome=nome,
                    telefone=telefone,
                    nome_responsavel=nome_responsavel if nome_responsavel else None,
                    telefone_responsavel=telefone_responsavel if telefone_responsavel else None,
                    data_nascimento=data_nascimento,
                    idade=idade,
                    cidade=cidade if cidade else None,
                    estado=estado if estado else None,
                    forma_pagamento=forma_pagamento,
                    dia_vencimento=dia_vencimento,
                    dublagem_online=request.form.get(f'dublagem_online_{i}') == 'on',
                    dublagem_presencial=request.form.get(f'dublagem_presencial_{i}') == 'on',
                    teatro_online=request.form.get(f'teatro_online_{i}') == 'on',
                    teatro_presencial=request.form.get(f'teatro_presencial_{i}') == 'on',
                    locucao=request.form.get(f'locucao_{i}') == 'on',
                    teatro_tv_cinema=request.form.get(f'teatro_tv_cinema_{i}') == 'on',
                    musical=request.form.get(f'musical_{i}') == 'on'
                )
                db.session.add(aluno)
                db.session.flush()
                
                # Criar matrículas
                for tipo_curso, dados in cursos_professores.items():
                    matricula = Matricula(
                        aluno_id=aluno.id,
                        professor_id=dados['professor_id'],
                        tipo_curso=tipo_curso,
                        valor_mensalidade=dados['valor_mensalidade']
                    )
                    db.session.add(matricula)
                
                alunos_cadastrados += 1
            
            if erros:
                db.session.rollback()
                for erro in erros:
                    flash(erro, 'error')
                return render_template('cadastro_alunos.html')
            
            db.session.commit()
            if alunos_cadastrados == 1:
                flash('Aluno cadastrado com sucesso!', 'success')
            else:
                flash(f'{alunos_cadastrados} alunos cadastrados com sucesso!', 'success')
            return redirect(url_for('main.cadastro_alunos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar alunos: {str(e)}', 'error')
            return render_template('cadastro_alunos.html')
    
    return render_template('cadastro_alunos.html')

@bp.route('/alunos')
def listar_alunos():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template('listar_alunos.html', alunos=alunos)

