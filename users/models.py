from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


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
