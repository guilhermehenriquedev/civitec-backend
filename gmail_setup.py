#!/usr/bin/env python
"""
Configuração rápida para Gmail
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

def setup_gmail():
    """Configura Gmail para envio de e-mails"""
    print("📧 CONFIGURAÇÃO RÁPIDA PARA GMAIL")
    print("=" * 40)
    print()
    
    # Verificar se já está configurado
    if settings.EMAIL_HOST == 'smtp.gmail.com':
        print("✅ Gmail já está configurado!")
        return
    
    print("🔧 Para configurar Gmail, siga estes passos:")
    print()
    print("1. ATIVE A VERIFICAÇÃO EM 2 ETAPAS:")
    print("   - Acesse: https://myaccount.google.com/security")
    print("   - Ative 'Verificação em duas etapas'")
    print()
    print("2. GERE UMA SENHA DE APP:")
    print("   - Acesse: https://myaccount.google.com/apppasswords")
    print("   - Selecione 'Email' e 'Outro (nome personalizado)'")
    print("   - Digite 'CiviTec' como nome")
    print("   - Clique em 'Gerar'")
    print("   - Copie a senha de 16 caracteres")
    print()
    print("3. ATUALIZE O ARQUIVO .env:")
    print("   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    print("   SMTP_HOST=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print("   SMTP_USER=seu_email@gmail.com")
    print("   SMTP_PASSWORD=sua_senha_de_app_16_caracteres")
    print("   SMTP_USE_TLS=True")
    print("   SMTP_USE_SSL=False")
    print()
    print("4. REINICIE O SERVIDOR DJANGO")
    print("   python manage.py runserver")
    print()
    print("5. TESTE ENVIANDO UM CONVITE")
    print("   - Acesse a página de usuários")
    print("   - Crie um novo convite")
    print("   - Verifique se o e-mail foi enviado")
    print()
    
    # Mostrar configuração atual
    print("🔍 CONFIGURAÇÃO ATUAL:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
    print()
    
    # Mostrar configuração desejada
    print("🎯 CONFIGURAÇÃO DESEJADA (Gmail):")
    print("   EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend")
    print("   EMAIL_HOST: smtp.gmail.com")
    print("   EMAIL_PORT: 587")
    print("   EMAIL_USE_TLS: True")
    print("   EMAIL_FROM: civitec@municipio.gov.br")
    print("   EMAIL_HOST_USER: [seu_email@gmail.com]")
    print("   EMAIL_HOST_PASSWORD: [sua_senha_de_app]")

if __name__ == '__main__':
    setup_gmail()




