from django.contrib import admin
from .models import WorkProject, WorkProgress, WorkPhoto


@admin.register(WorkProject)
class WorkProjectAdmin(admin.ModelAdmin):
    """Admin para obras/projetos"""
    list_display = ('name', 'status', 'budget', 'start_date', 'expected_end_date', 'responsible', 'created_at')
    list_filter = ('status', 'start_date', 'expected_end_date', 'created_at')
    search_fields = ('name', 'description', 'responsible', 'address')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identificação', {'fields': ('name', 'description', 'responsible')}),
        ('Localização', {'fields': ('address', 'location_lat', 'location_lng')}),
        ('Contrato', {'fields': ('contract',)}),
        ('Orçamento e Datas', {'fields': ('budget', 'start_date', 'expected_end_date', 'actual_end_date')}),
        ('Status', {'fields': ('status',)}),
    )


@admin.register(WorkProgress)
class WorkProgressAdmin(admin.ModelAdmin):
    """Admin para progresso das obras"""
    list_display = ('project', 'ref_month', 'physical_pct', 'financial_pct', 'created_at')
    list_filter = ('ref_month', 'created_at')
    search_fields = ('project__name', 'notes')
    ordering = ('project', '-ref_month')
    
    fieldsets = (
        ('Projeto', {'fields': ('project', 'ref_month')}),
        ('Progresso', {'fields': ('physical_pct', 'financial_pct')}),
        ('Observações', {'fields': ('notes',)}),
    )


@admin.register(WorkPhoto)
class WorkPhotoAdmin(admin.ModelAdmin):
    """Admin para fotos das obras"""
    list_display = ('project', 'title', 'taken_date', 'location', 'created_at')
    list_filter = ('taken_date', 'created_at')
    search_fields = ('title', 'description', 'project__name', 'location')
    ordering = ('project', '-taken_date')
    
    fieldsets = (
        ('Projeto', {'fields': ('project', 'title', 'description')}),
        ('Foto', {'fields': ('photo', 'taken_date', 'location')}),
    )
