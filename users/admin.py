from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserInvite


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin customizado para o modelo User"""
    
    list_display = [
        'email', 'first_name', 'last_name', 'role', 'sector', 
        'is_active', 'date_joined', 'last_login'
    ]
    list_filter = [
        'role', 'sector', 'is_active', 'date_joined', 'last_login'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['first_name', 'last_name']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'cpf')}),
        ('Permissões', {'fields': ('role', 'sector', 'is_active', 'is_staff', 'is_superuser')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Grupos', {'fields': ('groups',)}),
        ('Permissões de Usuário', {'fields': ('user_permissions',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'sector'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    """Admin para o modelo UserInvite"""
    
    list_display = [
        'email', 'full_name', 'role_code', 'sector_code', 'status',
        'created_at', 'expires_at', 'created_by', 'is_expired_display'
    ]
    list_filter = [
        'status', 'role_code', 'sector_code', 'created_at', 'expires_at'
    ]
    search_fields = ['email', 'full_name', 'token']
    ordering = ['-created_at']
    readonly_fields = [
        'security_code', 'token', 'created_at', 'updated_at', 
        'expires_at', 'accepted_at', 'is_expired_display'
    ]
    
    fieldsets = (
        ('Informações do Convite', {
            'fields': ('email', 'full_name', 'role_code', 'sector_code')
        }),
        ('Segurança', {
            'fields': ('security_code', 'token'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'expires_at', 'accepted_at', 'is_expired_display')
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired_display(self, obj):
        """Exibe se o convite está expirado"""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expirado</span>')
        return format_html('<span style="color: green;">Válido</span>')
    
    is_expired_display.short_description = 'Status de Expiração'
    
    def has_add_permission(self, request):
        """Apenas usuários master podem criar convites"""
        if request.user.is_authenticated:
            return request.user.is_master_admin
        return False
    
    def has_change_permission(self, request, obj=None):
        """Apenas usuários master podem alterar convites"""
        if request.user.is_authenticated:
            return request.user.is_master_admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Apenas usuários master podem deletar convites"""
        if request.user.is_authenticated:
            return request.user.is_master_admin
        return False
