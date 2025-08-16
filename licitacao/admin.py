from django.contrib import admin
from .models import Procurement, ProcPhase, Proposal, Award, Contract, ContractMilestone


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    """Admin para processos de licitação"""
    list_display = ('numero_processo', 'modalidade', 'status', 'valor_estimado', 'data_abertura', 'created_at')
    list_filter = ('modalidade', 'status', 'data_abertura', 'created_at')
    search_fields = ('numero_processo', 'objeto')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identificação', {'fields': ('modalidade', 'numero_processo', 'objeto')}),
        ('Valores e Datas', {'fields': ('valor_estimado', 'data_abertura', 'data_encerramento')}),
        ('Status', {'fields': ('status', 'observacoes')}),
    )


@admin.register(ProcPhase)
class ProcPhaseAdmin(admin.ModelAdmin):
    """Admin para fases do processo"""
    list_display = ('procurement', 'fase', 'start_dt', 'end_dt', 'status', 'created_at')
    list_filter = ('fase', 'status', 'start_dt', 'created_at')
    search_fields = ('procurement__numero_processo', 'fase')
    ordering = ('procurement', 'start_dt')
    
    fieldsets = (
        ('Processo', {'fields': ('procurement', 'fase')}),
        ('Período', {'fields': ('start_dt', 'end_dt')}),
        ('Status', {'fields': ('status', 'observacoes')}),
    )


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    """Admin para propostas"""
    list_display = ('supplier_name', 'procurement', 'valor', 'classificacao', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('supplier_name', 'supplier_doc', 'procurement__numero_processo')
    ordering = ('procurement', 'classificacao', 'valor')
    
    fieldsets = (
        ('Fornecedor', {'fields': ('supplier_name', 'supplier_doc')}),
        ('Proposta', {'fields': ('procurement', 'valor', 'classificacao')}),
        ('Status', {'fields': ('status', 'observacoes')}),
    )


@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    """Admin para adjudicações"""
    list_display = ('procurement', 'supplier', 'valor_adjudicado', 'homolog_dt', 'created_at')
    list_filter = ('homolog_dt', 'created_at')
    search_fields = ('procurement__numero_processo', 'supplier__supplier_name')
    ordering = ('-homolog_dt',)
    
    fieldsets = (
        ('Processo', {'fields': ('procurement', 'supplier')}),
        ('Adjudicação', {'fields': ('valor_adjudicado', 'homolog_dt')}),
        ('Observações', {'fields': ('observacoes',)}),
    )


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin para contratos"""
    list_display = ('number', 'supplier_name', 'status', 'valor_total', 'start_dt', 'end_dt', 'created_at')
    list_filter = ('status', 'start_dt', 'end_dt', 'created_at')
    search_fields = ('number', 'supplier_name', 'supplier_doc')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identificação', {'fields': ('number', 'procurement')}),
        ('Fornecedor', {'fields': ('supplier_name', 'supplier_doc')}),
        ('Período e Valores', {'fields': ('start_dt', 'end_dt', 'valor_total')}),
        ('Status', {'fields': ('status', 'objeto')}),
    )


@admin.register(ContractMilestone)
class ContractMilestoneAdmin(admin.ModelAdmin):
    """Admin para marcos do contrato"""
    list_display = ('contract', 'desc', 'due_dt', 'valor', 'status', 'created_at')
    list_filter = ('status', 'due_dt', 'created_at')
    search_fields = ('desc', 'contract__number')
    ordering = ('contract', 'due_dt')
    
    fieldsets = (
        ('Contrato', {'fields': ('contract', 'desc')}),
        ('Marco', {'fields': ('due_dt', 'valor', 'status')}),
        ('Observações', {'fields': ('observacoes',)}),
    )
