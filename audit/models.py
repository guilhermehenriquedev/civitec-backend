from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import User


class AuditLog(models.Model):
    """Modelo para log de auditoria de todas as ações CRUD"""
    
    class ActionChoices(models.TextChoices):
        CREATE = 'CREATE', 'Criar'
        READ = 'READ', 'Ler'
        UPDATE = 'UPDATE', 'Atualizar'
        DELETE = 'DELETE', 'Deletar'
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        APPROVE = 'APPROVE', 'Aprovar'
        REJECT = 'REJECT', 'Rejeitar'
        UPLOAD = 'UPLOAD', 'Upload'
        DOWNLOAD = 'DOWNLOAD', 'Download'
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuário'
    )
    action = models.CharField(
        max_length=20,
        choices=ActionChoices.choices,
        verbose_name='Ação'
    )
    entity = models.CharField(max_length=100, verbose_name='Entidade')
    entity_id = models.PositiveIntegerField(verbose_name='ID da Entidade')
    
    # Campos para referência genérica
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de Conteúdo'
    )
    object_id = models.PositiveIntegerField(verbose_name='ID do Objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    payload_json = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Payload JSON'
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name='Endereço IP'
    )
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    url = models.URLField(blank=True, verbose_name='URL')
    method = models.CharField(max_length=10, blank=True, verbose_name='Método HTTP')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['entity', 'entity_id', 'created_at']),
            models.Index(fields=['content_type', 'object_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.entity} #{self.entity_id} por {self.user} em {self.created_at}"
    
    @classmethod
    def log_action(cls, user, action, obj, payload=None, ip_address=None, user_agent=None, url=None, method=None):
        """
        Método de classe para facilitar o logging de ações
        
        Args:
            user: Usuário que executou a ação
            action: Tipo de ação (CREATE, UPDATE, DELETE, etc.)
            obj: Objeto que foi afetado
            payload: Dados adicionais em formato JSON
            ip_address: Endereço IP do usuário
            user_agent: User agent do navegador
            url: URL da requisição
            method: Método HTTP usado
        """
        if obj is None:
            return None
        
        content_type = ContentType.objects.get_for_model(obj)
        
        return cls.objects.create(
            user=user,
            action=action,
            entity=content_type.model,
            entity_id=obj.pk,
            content_type=content_type,
            object_id=obj.pk,
            payload_json=payload,
            ip_address=ip_address,
            user_agent=user_agent or '',
            url=url or '',
            method=method or ''
        )
    
    @classmethod
    def log_user_action(cls, user, action, entity, entity_id, payload=None, ip_address=None, user_agent=None, url=None, method=None):
        """
        Método de classe para logging de ações que não envolvem objetos específicos
        (ex: login, logout, etc.)
        """
        return cls.objects.create(
            user=user,
            action=action,
            entity=entity,
            entity_id=entity_id or 0,
            payload_json=payload,
            ip_address=ip_address,
            user_agent=user_agent or '',
            url=url or '',
            method=method or ''
        )
