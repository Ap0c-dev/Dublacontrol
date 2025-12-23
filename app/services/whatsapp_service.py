"""
Serviço para envio de notificações via WhatsApp usando Twilio
"""
from twilio.rest import Client
from datetime import date
from app.models.professor import db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Serviço para envio de mensagens WhatsApp via Twilio"""
    
    def __init__(self, account_sid, auth_token, from_number):
        """
        Inicializa o serviço WhatsApp
        
        Args:
            account_sid: Account SID do Twilio
            auth_token: Auth Token do Twilio
            from_number: Número de WhatsApp de origem (formato: whatsapp:+14155238886)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.client = None
        
        if account_sid and auth_token:
            try:
                self.client = Client(account_sid, auth_token)
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Twilio: {e}")
    
    def formatar_telefone(self, telefone):
        """
        Formata telefone para o formato do WhatsApp (whatsapp:+5511999999999)
        
        Args:
            telefone: Telefone no formato +55 11 987654321 ou similar
            
        Returns:
            Telefone formatado ou None se inválido
        """
        if not telefone:
            return None
        
        # Remove espaços e caracteres especiais
        telefone_limpo = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Se já começa com whatsapp:, retorna como está
        if telefone_limpo.startswith('whatsapp:'):
            return telefone_limpo
        
        # Se começa com +, adiciona whatsapp:
        if telefone_limpo.startswith('+'):
            return f'whatsapp:{telefone_limpo}'
        
        # Se não tem +, tenta adicionar (assumindo formato brasileiro)
        if telefone_limpo.startswith('55'):
            return f'whatsapp:+{telefone_limpo}'
        
        # Se começa com 0, remove e adiciona +55
        if telefone_limpo.startswith('0'):
            telefone_limpo = telefone_limpo[1:]
        
        # Se tem 11 dígitos (DDD + número), adiciona +55
        if len(telefone_limpo) == 11:
            return f'whatsapp:+55{telefone_limpo}'
        
        # Se tem 10 dígitos (sem 9 inicial), adiciona +55
        if len(telefone_limpo) == 10:
            return f'whatsapp:+55{telefone_limpo}'
        
        return None
    
    def criar_mensagem_vencimento(self, aluno, data_vencimento, valor_total):
        """
        Cria mensagem de notificação de vencimento
        
        Args:
            aluno: Objeto Aluno
            data_vencimento: Data de vencimento (date)
            valor_total: Valor total da mensalidade (float)
            
        Returns:
            Texto da mensagem formatada
        """
        data_formatada = data_vencimento.strftime('%d/%m/%Y')
        valor_formatado = f"R$ {valor_total:.2f}".replace('.', ',')
        
        # Obter modalidades do aluno
        modalidades = []
        if aluno.dublagem_online:
            modalidades.append("Dublagem Online")
        if aluno.dublagem_presencial:
            modalidades.append("Dublagem Presencial")
        if aluno.teatro_online:
            modalidades.append("Teatro Online")
        if aluno.teatro_presencial:
            modalidades.append("Teatro Presencial")
        if aluno.locucao:
            modalidades.append("Locução")
        if aluno.teatro_tv_cinema:
            modalidades.append("Teatro TV/Cinema")
        if aluno.musical:
            modalidades.append("Musical")
        
        modalidades_str = ", ".join(modalidades) if modalidades else "seus cursos"
        
        mensagem = f"""Olá, {aluno.nome}!

📅 Lembrete: Sua mensalidade vence hoje ({data_formatada}).

💰 Valor: {valor_formatado}
📚 Modalidades: {modalidades_str}

Para enviar o comprovante de pagamento, acesse o sistema.

Atenciosamente,
Equipe de Dublagem"""
        
        return mensagem
    
    def enviar_mensagem(self, telefone, mensagem):
        """
        Envia mensagem WhatsApp
        
        Args:
            telefone: Telefone do destinatário (formato: whatsapp:+5511999999999)
            mensagem: Texto da mensagem
            
        Returns:
            Tupla (sucesso: bool, resultado: dict com sid, status, erro)
        """
        if not self.client:
            return False, {"erro": "Cliente Twilio não inicializado"}
        
        telefone_formatado = self.formatar_telefone(telefone)
        if not telefone_formatado:
            return False, {"erro": f"Telefone inválido: {telefone}"}
        
        try:
            logger.info(f"Enviando mensagem WhatsApp. De: {self.from_number}, Para: {telefone_formatado}")
            
            message = self.client.messages.create(
                from_=self.from_number,
                body=mensagem,
                to=telefone_formatado
            )
            
            # Aguardar um pouco e verificar status
            import time
            time.sleep(1)  # Aguardar 1 segundo para status atualizar
            
            # Buscar status atualizado
            try:
                message = self.client.messages(message.sid).fetch()
                status = message.status
            except:
                status = "unknown"
            
            resultado = {
                "sid": message.sid,
                "status": status,
                "para": telefone_formatado,
                "de": self.from_number
            }
            
            logger.info(f"Mensagem WhatsApp enviada. SID: {message.sid}, Status: {status}, Para: {telefone_formatado}")
            
            # Verificar se status indica problema
            if status in ['failed', 'undelivered', 'canceled']:
                return False, {**resultado, "erro": f"Status: {status}. Verifique se o número está aprovado no Sandbox."}
            
            return True, resultado
            
        except Exception as e:
            erro_msg = str(e)
            logger.error(f"Erro ao enviar mensagem WhatsApp para {telefone_formatado}: {erro_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, {"erro": erro_msg, "telefone": telefone_formatado}
    
    def notificar_vencimentos_hoje(self):
        """
        Envia notificações para todos os alunos com vencimento hoje
        
        Returns:
            Dicionário com estatísticas: {'enviadas': int, 'erros': int, 'detalhes': list}
        """
        if not self.client:
            logger.warning("WhatsApp não configurado ou desabilitado")
            return {'enviadas': 0, 'erros': 0, 'detalhes': []}
        
        hoje = date.today()
        resultados = {
            'enviadas': 0,
            'erros': 0,
            'detalhes': []
        }
        
        # Buscar alunos com vencimento hoje e que estão ativos
        alunos = Aluno.query.filter(
            Aluno.data_vencimento == hoje,
            Aluno.ativo == True
        ).all()
        
        logger.info(f"Encontrados {len(alunos)} alunos com vencimento hoje")
        
        for aluno in alunos:
            # Verificar se tem telefone
            telefone = aluno.telefone or aluno.telefone_responsavel
            if not telefone:
                resultados['detalhes'].append({
                    'aluno': aluno.nome,
                    'status': 'erro',
                    'mensagem': 'Telefone não cadastrado'
                })
                resultados['erros'] += 1
                continue
            
            # Calcular valor total das mensalidades
            valor_total = aluno.get_total_mensalidades()
            
            # Criar mensagem
            mensagem = self.criar_mensagem_vencimento(aluno, aluno.data_vencimento, valor_total)
            
            # Enviar mensagem
            sucesso, resultado = self.enviar_mensagem(telefone, mensagem)
            
            if sucesso:
                resultados['enviadas'] += 1
                resultados['detalhes'].append({
                    'aluno': aluno.nome,
                    'telefone': telefone,
                    'status': 'enviada',
                    'mensagem_id': resultado.get('sid') if isinstance(resultado, dict) else resultado,
                    'status_twilio': resultado.get('status') if isinstance(resultado, dict) else 'N/A'
                })
            else:
                resultados['erros'] += 1
                erro_msg = resultado.get('erro') if isinstance(resultado, dict) else resultado
                resultados['detalhes'].append({
                    'aluno': aluno.nome,
                    'telefone': telefone,
                    'status': 'erro',
                    'mensagem': erro_msg,
                    'status_twilio': resultado.get('status') if isinstance(resultado, dict) else 'N/A'
                })
        
        logger.info(f"Notificações enviadas: {resultados['enviadas']}, Erros: {resultados['erros']}")
        return resultados

