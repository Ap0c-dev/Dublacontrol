#!/bin/bash
# Script para iniciar backend (Flask) e frontend (React) simultaneamente

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando servidores de desenvolvimento...${NC}"

# Verificar se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não detectado. Ativando...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"
    else
        echo -e "${RED}❌ Ambiente virtual não encontrado. Execute: python3 -m venv venv${NC}"
        exit 1
    fi
fi

# Função para limpar processos ao sair
cleanup() {
    echo -e "\n${YELLOW}🛑 Parando servidores...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Iniciar backend Flask
echo -e "${BLUE}📦 Iniciando backend Flask na porta 5000...${NC}"
cd "$(dirname "$0")"
python wsgi.py > /tmp/flask-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"

# Aguardar backend iniciar
sleep 2

# Verificar se o backend está rodando
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Erro ao iniciar backend. Verifique os logs:${NC}"
    cat /tmp/flask-backend.log
    exit 1
fi

# Iniciar frontend React
echo -e "${BLUE}⚛️  Iniciando frontend React...${NC}"
cd frontend_lovable/connect-dashboard-main

# Carregar nvm se disponível
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Verificar se node está instalado
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado. Instale Node.js primeiro.${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar frontend
npm run dev > /tmp/react-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

echo -e "\n${GREEN}✅ Servidores iniciados com sucesso!${NC}"
echo -e "${BLUE}📊 Backend: http://localhost:5000${NC}"
echo -e "${BLUE}📊 Frontend: http://localhost:5173 (ou porta configurada no Vite)${NC}"
echo -e "${YELLOW}💡 Pressione Ctrl+C para parar ambos os servidores${NC}\n"

# Aguardar processos
wait

