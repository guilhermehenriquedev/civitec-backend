"""
Serviços para o módulo de usuários
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserInvite


def send_invite_email(invite: UserInvite):
    """
    Envia e-mail de convite para o usuário
    """
    subject = "Você foi convidado para o CiviTec"
    
    # Contexto para o template
    context = {
        'full_name': invite.full_name,
        'security_code': invite.security_code,
        'invite_url': invite.get_invite_url(),
        'expires_hours': getattr(settings, 'INVITE_EXPIRES_HOURS', 72),
        'role_display': invite.get_role_code_display(),
        'sector_display': invite.get_sector_code_display() if invite.sector_code else 'Não definido',
    }
    
    # Renderizar template HTML
    html_message = render_to_string('users/emails/invite.html', context)
    
    # Renderizar versão texto simples
    text_message = render_to_string('users/emails/invite.txt', context)
    
    # Enviar e-mail
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.EMAIL_FROM,
        recipient_list=[invite.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    """
    Envia e-mail de boas-vindas após aceitar convite
    """
    subject = "Bem-vindo ao CiviTec!"
    
    context = {
        'full_name': user.get_full_name(),
        'role_display': user.get_role_display(),
        'sector_display': user.get_sector_display() if user.sector else 'Não definido',
    }
    
    html_message = render_to_string('users/emails/welcome.html', context)
    text_message = render_to_string('users/emails/welcome.txt', context)
    
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.EMAIL_FROM,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
