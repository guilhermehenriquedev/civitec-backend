from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para logs de auditoria"""
    list_display = ('user', 'action', 'entity', 'entity_id', 'ip_address', 'created_at')
    list_filter = ('action', 'entity', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'entity', 'ip_address')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Usuário e Ação', {'fields': ('user', 'action')}),
        ('Entidade', {'fields': ('entity', 'entity_id', 'content_type', 'object_id')}),
        ('Detalhes da Requisição', {'fields': ('ip_address', 'user_agent', 'url', 'method')}),
        ('Payload', {'fields': ('payload_json',)}),
    )
    
    readonly_fields = ('created_at', 'user', 'action', 'entity', 'entity_id', 'content_type', 'object_id', 'payload_json', 'ip_address', 'user_agent', 'url', 'method')
    
    def has_add_permission(self, request):
        """Não permite adicionar logs manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Não permite editar logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permite deletar logs apenas para superusuários"""
        return request.user.is_superuser
