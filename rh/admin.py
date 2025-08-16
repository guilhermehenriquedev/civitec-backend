from django.contrib import admin
from .models import Employee, VacationRequest, Payslip


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin para funcionários"""
    list_display = ('user', 'matricula', 'cargo', 'lotacao', 'regime', 'status', 'admissao_dt')
    list_filter = ('regime', 'status', 'admissao_dt')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'matricula')
    ordering = ('user__first_name', 'user__last_name')
    
    fieldsets = (
        ('Informações do Usuário', {'fields': ('user',)}),
        ('Informações Funcionais', {'fields': ('matricula', 'cargo', 'lotacao', 'regime', 'admissao_dt', 'status')}),
    )


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    """Admin para solicitações de férias"""
    list_display = ('employee', 'period_start', 'period_end', 'days_requested', 'status', 'created_at')
    list_filter = ('status', 'period_start', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__matricula')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Solicitação', {'fields': ('employee', 'period_start', 'period_end', 'days_requested', 'reason')}),
        ('Aprovação', {'fields': ('status', 'approver', 'approved_at', 'rejection_reason')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    """Admin para contracheques"""
    list_display = ('employee', 'competencia', 'bruto', 'descontos', 'liquido', 'created_at')
    list_filter = ('competencia', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__matricula')
    ordering = ('-competencia', 'employee__user__first_name')
    
    fieldsets = (
        ('Funcionário', {'fields': ('employee', 'competencia')}),
        ('Valores', {'fields': ('bruto', 'descontos', 'liquido')}),
        ('Arquivo', {'fields': ('pdf_url', 'pdf_file')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
