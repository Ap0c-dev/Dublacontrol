#!/usr/bin/env python3
"""
Script para migrar dados do banco antigo (banco_lucy) para o banco de dev (banco_lucy_dev)
"""

import sqlite3
import os
from datetime import datetime
from app import create_app
from app.models.professor import Professor, db
from app.models.aluno import Aluno
from app.models.matricula import Matricula

def migrar_dados():
    """Migra dados do banco antigo para o banco de dev"""
    banco_antigo = '/home/tiago/banco_lucy'
    banco_dev = '/home/tiago/banco_lucy_dev'
    
    if not os.path.exists(banco_antigo):
        print(f"✗ Banco antigo não encontrado: {banco_antigo}")
        return
    
    print("=" * 60)
    print("MIGRAÇÃO DE DADOS DO BANCO ANTIGO PARA DEV")
    print("=" * 60)
    
    # Conectar ao banco antigo
    conn_antigo = sqlite3.connect(banco_antigo)
    cursor_antigo = conn_antigo.cursor()
    
    # Criar app e conectar ao banco de dev
    app = create_app()
    with app.app_context():
        # Verificar se já existem dados no banco de dev
        professores_existentes = Professor.query.count()
        alunos_existentes = Aluno.query.count()
        
        if professores_existentes > 0 or alunos_existentes > 0:
            resposta = input(f"\n⚠️  O banco de dev já tem {professores_existentes} professores e {alunos_existentes} alunos.\nDeseja continuar? (s/N): ")
            if resposta.lower() != 's':
                print("Migração cancelada.")
                return
        
        # Migrar professores
        print("\n--- Migrando Professores ---")
        cursor_antigo.execute("SELECT id, nome, telefone, dublagem_presencial, dublagem_online, teatro_presencial, teatro_online, musical, locucao, curso_apresentador, data_cadastro FROM professores")
        professores_antigos = cursor_antigo.fetchall()
        
        professores_migrados = 0
        for prof in professores_antigos:
            try:
                # Verificar se já existe
                existe = Professor.query.filter_by(nome=prof[1], telefone=prof[2]).first()
                if existe:
                    print(f"  ⚠️  Professor '{prof[1]}' já existe, pulando...")
                    continue
                
                novo_professor = Professor(
                    nome=prof[1],
                    telefone=prof[2],
                    dublagem_presencial=bool(prof[3]) if prof[3] is not None else False,
                    dublagem_online=bool(prof[4]) if prof[4] is not None else False,
                    teatro_presencial=bool(prof[5]) if prof[5] is not None else False,
                    teatro_online=bool(prof[6]) if prof[6] is not None else False,
                    musical=bool(prof[7]) if prof[7] is not None else False,
                    locucao=bool(prof[8]) if prof[8] is not None else False,
                    curso_apresentador=bool(prof[9]) if prof[9] is not None else False
                )
                db.session.add(novo_professor)
                professores_migrados += 1
                print(f"  ✓ Professor '{prof[1]}' migrado")
            except Exception as e:
                print(f"  ✗ Erro ao migrar professor '{prof[1]}': {e}")
        
        # Commit dos professores antes de migrar alunos
        if professores_migrados > 0:
            try:
                db.session.commit()
                print(f"\n✓ {professores_migrados} professores salvos com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"\n✗ Erro ao salvar professores: {e}")
                return
        
        # Migrar alunos
        print("\n--- Migrando Alunos ---")
        try:
            cursor_antigo.execute("SELECT id, nome, telefone, nome_responsavel, telefone_responsavel, data_nascimento, idade, rua, numero, bairro, cidade, pais, dublagem_online, dublagem_presencial, teatro_online, teatro_presencial, locucao, teatro_tv_cinema, musical, data_cadastro FROM alunos")
            alunos_antigos = cursor_antigo.fetchall()
            
            alunos_migrados = 0
            for aluno_data in alunos_antigos:
                try:
                    # Verificar se já existe
                    existe = Aluno.query.filter_by(nome=aluno_data[1], telefone=aluno_data[2]).first()
                    if existe:
                        print(f"  ⚠️  Aluno '{aluno_data[1]}' já existe, pulando...")
                        continue
                    
                    # Converter data_nascimento de string para date se necessário
                    data_nasc = None
                    if aluno_data[5]:
                        if isinstance(aluno_data[5], str):
                            try:
                                data_nasc = datetime.strptime(aluno_data[5], '%Y-%m-%d').date()
                            except:
                                try:
                                    data_nasc = datetime.strptime(aluno_data[5], '%Y/%m/%d').date()
                                except:
                                    data_nasc = None
                        else:
                            data_nasc = aluno_data[5]
                    
                    novo_aluno = Aluno(
                        nome=aluno_data[1],
                        telefone=aluno_data[2],
                        nome_responsavel=aluno_data[3] if aluno_data[3] else None,
                        telefone_responsavel=aluno_data[4] if aluno_data[4] else None,
                        data_nascimento=data_nasc,
                        idade=aluno_data[6] if aluno_data[6] else None,
                        rua=aluno_data[7] if aluno_data[7] else None,
                        numero=aluno_data[8] if aluno_data[8] else None,
                        bairro=aluno_data[9] if aluno_data[9] else None,
                        cidade=aluno_data[10] if aluno_data[10] else None,
                        pais=aluno_data[11] if aluno_data[11] else None,
                        dublagem_online=bool(aluno_data[12]) if aluno_data[12] is not None else False,
                        dublagem_presencial=bool(aluno_data[13]) if aluno_data[13] is not None else False,
                        teatro_online=bool(aluno_data[14]) if aluno_data[14] is not None else False,
                        teatro_presencial=bool(aluno_data[15]) if aluno_data[15] is not None else False,
                        locucao=bool(aluno_data[16]) if aluno_data[16] is not None else False,
                        teatro_tv_cinema=bool(aluno_data[17]) if aluno_data[17] is not None else False,
                        musical=bool(aluno_data[18]) if aluno_data[18] is not None else False
                    )
                    db.session.add(novo_aluno)
                    alunos_migrados += 1
                    print(f"  ✓ Aluno '{aluno_data[1]}' migrado")
                except Exception as e:
                    print(f"  ✗ Erro ao migrar aluno '{aluno_data[1]}': {e}")
        except sqlite3.OperationalError as e:
            print(f"  ⚠️  Tabela 'alunos' não encontrada ou estrutura diferente: {e}")
        
        # Commit das alterações
        try:
            db.session.commit()
            print(f"\n✓ Migração concluída!")
            print(f"  - {professores_migrados} professores migrados")
            print(f"  - {alunos_migrados} alunos migrados")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Erro ao salvar migração: {e}")
            import traceback
            traceback.print_exc()
    
    conn_antigo.close()
    print("\n" + "=" * 60)

if __name__ == '__main__':
    migrar_dados()

