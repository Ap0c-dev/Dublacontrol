#!/bin/bash
# Script para iniciar o frontend com nvm carregado

# Carregar nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Verificar se node está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instalando..."
    nvm install --lts
fi

# Iniciar o servidor de desenvolvimento
echo "🚀 Iniciando servidor de desenvolvimento..."
npm run dev

