#!/usr/bin/env python3
"""
Script para enviar notificações WhatsApp de vencimentos
Executar via cron job diariamente

Uso:
    python enviar_notificacoes.py

Ou adicionar ao crontab:
    0 9 * * * cd /caminho/do/projeto && /usr/bin/python3 enviar_notificacoes.py
    (Executa todo dia às 9h)
"""
import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.whatsapp_service import WhatsAppService
from datetime import date
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notificacoes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal para enviar notificações"""
    app = create_app()
    
    with app.app_context():
        # Verificar se WhatsApp está habilitado
        if not app.config.get('WHATSAPP_ENABLED', False):
            logger.warning("WhatsApp não está habilitado. Configure WHATSAPP_ENABLED=true")
            return
        
        # Verificar credenciais
        account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        from_number = app.config.get('TWILIO_WHATSAPP_FROM')
        
        if not account_sid or not auth_token:
            logger.error("Credenciais do Twilio não configuradas")
            return
        
        logger.info("Iniciando envio de notificações de vencimento...")
        logger.info(f"Data de hoje: {date.today()}")
        
        # Inicializar serviço WhatsApp
        whatsapp = WhatsAppService(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number
        )
        
        # Enviar notificações
        resultados = whatsapp.notificar_vencimentos_hoje()
        
        # Log dos resultados
        logger.info(f"Notificações enviadas: {resultados['enviadas']}")
        logger.info(f"Erros: {resultados['erros']}")
        
        if resultados['detalhes']:
            for detalhe in resultados['detalhes']:
                if detalhe['status'] == 'enviada':
                    logger.info(f"✅ {detalhe['aluno']}: Enviada (ID: {detalhe.get('mensagem_id', 'N/A')})")
                else:
                    logger.warning(f"❌ {detalhe['aluno']}: {detalhe.get('mensagem', 'Erro desconhecido')}")
        
        logger.info("Processo de notificações concluído")

if __name__ == '__main__':
    main()

