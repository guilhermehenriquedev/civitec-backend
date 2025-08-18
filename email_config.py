"""
Configurações de e-mail para diferentes provedores
"""
import os

# Configurações para Gmail
GMAIL_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': 'seu_email@gmail.com',  # Substitua pelo seu e-mail
    'EMAIL_HOST_PASSWORD': 'sua_senha_de_app',  # Substitua pela senha de app
}

# Configurações para Outlook/Hotmail
OUTLOOK_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp-mail.outlook.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': 'seu_email@outlook.com',  # Substitua pelo seu e-mail
    'EMAIL_HOST_PASSWORD': 'sua_senha',  # Substitua pela sua senha
}

# Configurações para Yahoo
YAHOO_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'smtp.mail.yahoo.com',
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': 'seu_email@yahoo.com',  # Substitua pelo seu e-mail
    'EMAIL_HOST_PASSWORD': 'sua_senha_de_app',  # Substitua pela senha de app
}

# Configurações para servidor próprio
CUSTOM_SMTP_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': 'seu_servidor_smtp.com',  # Substitua pelo seu servidor
    'EMAIL_PORT': 587,
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': 'seu_usuario',  # Substitua pelo seu usuário
    'EMAIL_HOST_PASSWORD': 'sua_senha',  # Substitua pela sua senha
}

# Configuração atual (console para desenvolvimento)
CURRENT_CONFIG = {
    'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
    'EMAIL_FROM': 'civitec@municipio.gov.br',
}

def get_email_config(provider='console'):
    """
    Retorna a configuração de e-mail para o provedor especificado
    
    Args:
        provider (str): 'console', 'gmail', 'outlook', 'yahoo', 'custom'
    
    Returns:
        dict: Configuração de e-mail
    """
    configs = {
        'console': CURRENT_CONFIG,
        'gmail': GMAIL_CONFIG,
        'outlook': OUTLOOK_CONFIG,
        'yahoo': YAHOO_CONFIG,
        'custom': CUSTOM_SMTP_CONFIG,
    }
    
    if provider not in configs:
        print(f"❌ Provedor '{provider}' não suportado. Usando console.")
        return CURRENT_CONFIG
    
    config = configs[provider].copy()
    
    # Adicionar configurações padrão
    if provider != 'console':
        config['EMAIL_FROM'] = 'civitec@municipio.gov.br'
    
    return config

def print_email_instructions():
    """Imprime instruções para configurar e-mail"""
    print("📧 INSTRUÇÕES PARA CONFIGURAR E-MAIL:")
    print("=" * 50)
    print()
    print("1. ESCOLHA UM PROVEDOR:")
    print("   - Gmail: Para contas Google")
    print("   - Outlook: Para contas Microsoft")
    print("   - Yahoo: Para contas Yahoo")
    print("   - Custom: Para servidores próprios")
    print()
    print("2. PARA GMAIL:")
    print("   - Ative a verificação em 2 etapas")
    print("   - Gere uma senha de app")
    print("   - Use a senha de app no EMAIL_HOST_PASSWORD")
    print()
    print("3. PARA OUTLOOK:")
    print("   - Use sua senha normal")
    print("   - Pode precisar ativar 'Acesso a app menos seguro'")
    print()
    print("4. ATUALIZE O ARQUIVO email_config.py:")
    print("   - Substitua os valores de exemplo pelos seus")
    print("   - Reinicie o servidor Django")
    print()
    print("5. TESTE COM:")
    print("   python email_config.py")
    print()
    print("6. PARA PRODUÇÃO:")
    print("   - Use variáveis de ambiente (.env)")
    print("   - Nunca commite senhas no código")
    print()

if __name__ == '__main__':
    print_email_instructions()
    
    # Testar configuração atual
    print("🔍 TESTANDO CONFIGURAÇÃO ATUAL:")
    current = get_email_config('console')
    for key, value in current.items():
        print(f"   {key}: {value}")
    
    print()
    print("🔍 TESTANDO CONFIGURAÇÃO GMAIL (exemplo):")
    gmail = get_email_config('gmail')
    for key, value in gmail.items():
        if 'PASSWORD' in key:
            print(f"   {key}: {'*' * 8}")
        else:
            print(f"   {key}: {value}")


