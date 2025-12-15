#!/usr/bin/env python3
"""Script para testar se as credenciais do Cloudinary estão sendo carregadas corretamente"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

# Carregar .env
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Arquivo .env carregado: {env_path}")
    else:
        print(f"✗ Arquivo .env não encontrado em: {env_path}")
        sys.exit(1)
except ImportError:
    print("✗ python-dotenv não instalado. Execute: pip install python-dotenv")
    sys.exit(1)

# Verificar variáveis
print("\n=== Verificação de Variáveis de Ambiente ===")
cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
api_key = os.environ.get('CLOUDINARY_API_KEY')
api_secret = os.environ.get('CLOUDINARY_API_SECRET')

print(f"CLOUDINARY_CLOUD_NAME: {cloud_name if cloud_name else '✗ NÃO DEFINIDO'}")
print(f"CLOUDINARY_API_KEY: {'✓ DEFINIDO (' + str(len(api_key)) + ' caracteres)' if api_key else '✗ NÃO DEFINIDO'}")
print(f"CLOUDINARY_API_SECRET: {'✓ DEFINIDO (' + str(len(api_secret)) + ' caracteres)' if api_secret else '✗ NÃO DEFINIDO'}")

if not cloud_name or not api_key or not api_secret:
    print("\n✗ ERRO: Algumas credenciais estão faltando!")
    sys.exit(1)

# Testar importação do Config
print("\n=== Teste de Importação do Config ===")
try:
    from config import Config
    print(f"✓ Config importado com sucesso")
    print(f"  Config.CLOUDINARY_CLOUD_NAME: {Config.CLOUDINARY_CLOUD_NAME}")
    print(f"  Config.CLOUDINARY_API_KEY: {'✓ DEFINIDO' if Config.CLOUDINARY_API_KEY else '✗ VAZIO'}")
    print(f"  Config.CLOUDINARY_API_SECRET: {'✓ DEFINIDO' if Config.CLOUDINARY_API_SECRET else '✗ VAZIO'}")
except Exception as e:
    print(f"✗ Erro ao importar Config: {e}")
    sys.exit(1)

# Testar configuração do Cloudinary
print("\n=== Teste de Configuração do Cloudinary ===")
try:
    import cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    print("✓ Cloudinary configurado com sucesso")
    
    # Teste simples de conexão
    try:
        result = cloudinary.api.ping()
        print("✓ Conexão com Cloudinary OK")
    except Exception as e:
        print(f"⚠️  Aviso ao testar conexão: {e}")
        
except Exception as e:
    print(f"✗ Erro ao configurar Cloudinary: {e}")
    sys.exit(1)

print("\n✓ Todas as verificações passaram!")

