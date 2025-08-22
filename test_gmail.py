#!/usr/bin/env python
"""
Teste de envio de e-mail via Gmail
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail():
    """Testa o envio de e-mail via Gmail"""
    print("🔍 Testando configuração de Gmail...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_FROM: {settings.EMAIL_FROM}")
    print()
    
    try:
        # Testar envio de e-mail via Gmail
        print("📧 Enviando e-mail de teste via Gmail...")
        
        send_mail(
            subject='Teste de E-mail CiviTec - Gmail',
            message='Este é um e-mail de teste para verificar se a configuração do Gmail está funcionando.',
            from_email=settings.EMAIL_FROM,
            recipient_list=['guilhermehenrique@gmail.com'],  # Enviar para você mesmo
            fail_silently=False,
        )
        
        print("✅ E-mail enviado com sucesso via Gmail!")
        print("📧 Verifique sua caixa de entrada: guilhermehenrique@gmail.com")
        
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Dicas de solução
        print()
        print("🔧 POSSÍVEIS SOLUÇÕES:")
        print("1. Verifique se a verificação em 2 etapas está ativa")
        print("2. Confirme se a senha de app está correta")
        print("3. Verifique se não há bloqueios de segurança")
        print("4. Tente acessar: https://myaccount.google.com/security")

if __name__ == '__main__':
    test_gmail()




