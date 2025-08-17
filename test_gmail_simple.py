#!/usr/bin/env python
"""
Teste simples de conexão SMTP com Gmail
"""
import smtplib
import ssl

def test_smtp_connection():
    """Testa apenas a conexão SMTP"""
    print("🔍 Testando conexão SMTP com Gmail...")
    
    # Configurações
    smtp_server = "smtp.gmail.com"
    port = 587
    username = "guilhermehenrique@gmail.com"
    password = "ttqg uzxp amky cgsg"
    
    try:
        # Criar contexto SSL
        context = ssl.create_default_context()
        
        # Tentar conectar
        print(f"📡 Conectando ao {smtp_server}:{port}...")
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        
        print("🔐 Tentando fazer login...")
        server.login(username, password)
        
        print("✅ Login bem-sucedido!")
        print("📧 Conexão SMTP funcionando!")
        
        # Fechar conexão
        server.quit()
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erro de autenticação: {e}")
        print()
        print("🔧 SOLUÇÕES:")
        print("1. Verifique se a verificação em 2 etapas está ativa")
        print("2. Gere uma nova senha de app")
        print("3. Confirme se o e-mail está correto")
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print()
        print("🔧 POSSÍVEIS CAUSAS:")
        print("1. Problema de rede")
        print("2. Firewall bloqueando")
        print("3. Configurações incorretas")

if __name__ == '__main__':
    test_smtp_connection()
