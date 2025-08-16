from django.contrib import admin
from .models import Taxpayer, Invoice, Assessment, Billing


@admin.register(Taxpayer)
class TaxpayerAdmin(admin.ModelAdmin):
    """Admin para contribuintes"""
    list_display = ('name', 'doc', 'type', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('name', 'doc', 'email')
    ordering = ('name',)
    
    fieldsets = (
        ('Identificação', {'fields': ('name', 'doc', 'type')}),
        ('Contato', {'fields': ('address', 'phone', 'email')}),
        ('Status', {'fields': ('is_active',)}),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin para notas fiscais"""
    list_display = ('number', 'taxpayer', 'issue_dt', 'amount', 'status', 'created_at')
    list_filter = ('status', 'issue_dt', 'created_at')
    search_fields = ('number', 'taxpayer__name', 'service_code')
    ordering = ('-issue_dt', 'number')
    
    fieldsets = (
        ('Identificação', {'fields': ('number', 'taxpayer', 'issue_dt')}),
        ('Serviço', {'fields': ('service_code', 'description', 'amount')}),
        ('Status', {'fields': ('status',)}),
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin para avaliações/guias"""
    list_display = ('taxpayer', 'tax_kind', 'competence', 'principal', 'total', 'status', 'created_at')
    list_filter = ('tax_kind', 'status', 'competence', 'created_at')
    search_fields = ('taxpayer__name', 'taxpayer__doc')
    ordering = ('-competence', 'taxpayer__name')
    
    fieldsets = (
        ('Contribuinte', {'fields': ('taxpayer', 'tax_kind', 'competence')}),
        ('Valores', {'fields': ('principal', 'multa', 'juros', 'total')}),
        ('Status', {'fields': ('status',)}),
    )
    
    readonly_fields = ('total',)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    """Admin para cobranças"""
    list_display = ('assessment', 'due_dt', 'amount', 'status', 'payment_dt', 'created_at')
    list_filter = ('status', 'due_dt', 'payment_dt', 'created_at')
    search_fields = ('barcode', 'assessment__taxpayer__name')
    ordering = ('due_dt', 'assessment__taxpayer__name')
    
    fieldsets = (
        ('Avaliação', {'fields': ('assessment',)}),
        ('Cobrança', {'fields': ('due_dt', 'barcode', 'amount', 'status')}),
        ('Pagamento', {'fields': ('payment_dt', 'payment_amount')}),
    )
