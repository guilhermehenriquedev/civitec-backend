from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


class User(AbstractUser):
    """
    Modelo de usuário customizado com sistema de roles e setores
    """
    
    # Choices para roles
    class RoleChoices(models.TextChoices):
        MASTER_ADMIN = 'MASTER_ADMIN', 'Administrador Master'
        SECTOR_ADMIN = 'SECTOR_ADMIN', 'Administrador de Setor'
        SECTOR_OPERATOR = 'SECTOR_OPERATOR', 'Operador de Setor'
        EMPLOYEE = 'EMPLOYEE', 'Funcionário'
    
    # Choices para setores
    class SectorChoices(models.TextChoices):
        RH = 'RH', 'Recursos Humanos'
        TRIBUTOS = 'TRIBUTOS', 'Tributos'
        LICITACAO = 'LICITACAO', 'Licitação'
        OBRAS = 'OBRAS', 'Obras'
    
    # Campos customizados
    cpf = models.CharField(
        max_length=14, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ],
        verbose_name='CPF'
    )
    
    # Campos obrigatórios
    email = models.EmailField(unique=True, verbose_name='E-mail')
    first_name = models.CharField(max_length=150, verbose_name='Nome')
    last_name = models.CharField(max_length=150, verbose_name='Sobrenome')
    
    # Campos de role e setor
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.EMPLOYEE,
        verbose_name='Papel'
    )
    
    sector = models.CharField(
        max_length=20,
        choices=SectorChoices.choices,
        blank=True,
        null=True,
        verbose_name='Setor'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    # Configurações
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_master_admin(self):
        return self.role == self.RoleChoices.MASTER_ADMIN
    
    @property
    def is_sector_admin(self):
        return self.role == self.RoleChoices.SECTOR_ADMIN
    
    @property
    def is_sector_operator(self):
        return self.role == self.RoleChoices.SECTOR_OPERATOR
    
    @property
    def is_employee(self):
        return self.role == self.RoleChoices.EMPLOYEE
    
    def can_access_sector(self, sector_code):
        """Verifica se o usuário pode acessar um setor específico"""
        if self.is_master_admin:
            return True
        return self.sector == sector_code
    
    def get_permissions(self):
        """Retorna as permissões baseadas no role"""
        if self.is_master_admin:
            return ['*']  # Todas as permissões
        
        permissions = []
        if self.is_sector_admin or self.is_sector_operator:
            permissions.extend(['read', 'create', 'update'])
            if self.is_sector_admin:
                permissions.append('delete')
        
        if self.is_employee:
            permissions.extend(['read_own', 'update_own'])
        
        return permissions


class UserInvite(models.Model):
    """
    Modelo para gerenciar convites de usuários
    """
    
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        EXPIRED = 'EXPIRED', 'Expirado'
        ACCEPTED = 'ACCEPTED', 'Aceito'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    # Campos básicos
    email = models.EmailField(verbose_name='E-mail')
    full_name = models.CharField(max_length=255, verbose_name='Nome Completo')
    role_code = models.CharField(
        max_length=20,
        choices=User.RoleChoices.choices,
        verbose_name='Papel'
    )
    sector_code = models.CharField(
        max_length=20,
        choices=User.SectorChoices.choices,
        blank=True,
        null=True,
        verbose_name='Setor'
    )
    
    # Campos de segurança
    security_code = models.CharField(max_length=8, verbose_name='Código de Segurança')
    token = models.CharField(max_length=64, unique=True, verbose_name='Token de Convite')
    
    # Campos de controle
    expires_at = models.DateTimeField(verbose_name='Expira em')
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name='Aceito em')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name='Status'
    )
    
    # Campos de auditoria
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invites_sent',
        verbose_name='Criado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Convite de Usuário'
        verbose_name_plural = 'Convites de Usuários'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['token']),
            models.Index(fields=['security_code']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Convite para {self.full_name} ({self.email})"
    
    def save(self, *args, **kwargs):
        print(f"🔍 DEBUG: UserInvite.save chamado - PK: {self.pk}")
        print(f"🔍 DEBUG: Dados: email={self.email}, nome={self.full_name}, role={self.role_code}")
        
        if not self.pk:  # Novo convite
            print("🔍 DEBUG: Criando novo convite...")
            if not self.security_code:
                self.security_code = self._generate_security_code()
                print(f"🔍 DEBUG: Security code gerado: {self.security_code}")
            if not self.token:
                self.token = self._generate_token()
                print(f"🔍 DEBUG: Token gerado: {self.token}")
            if not self.expires_at:
                self.expires_at = timezone.now() + timedelta(
                    hours=getattr(settings, 'INVITE_EXPIRES_HOURS', 72)
                )
                print(f"🔍 DEBUG: Expires at definido: {self.expires_at}")
        
        try:
            super().save(*args, **kwargs)
            print(f"✅ DEBUG: UserInvite salvo com sucesso - ID: {self.id}")
        except Exception as e:
            print(f"❌ DEBUG: Erro ao salvar UserInvite: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _generate_security_code(self):
        """Gera um código de segurança de 6 dígitos"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def _generate_token(self):
        """Gera um token único para o convite"""
        return secrets.token_urlsafe(32)
    
    @property
    def is_expired(self):
        """Verifica se o convite expirou"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Verifica se o convite é válido para uso"""
        return (
            self.status == self.StatusChoices.PENDING and 
            not self.is_expired
        )
    
    def accept(self):
        """Marca o convite como aceito"""
        self.status = self.StatusChoices.ACCEPTED
        self.accepted_at = timezone.now()
        self.save()
    
    def expire(self):
        """Marca o convite como expirado"""
        self.status = self.StatusChoices.EXPIRED
        self.save()
    
    def cancel(self):
        """Cancela o convite"""
        self.status = self.StatusChoices.CANCELLED
        self.save()
    
    def get_invite_url(self):
        """Retorna a URL para aceitar o convite"""
        base_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000')
        return f"{base_url}/convite/criar-senha?token={self.token}"
