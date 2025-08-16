from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class WorkProject(models.Model):
    """Modelo para obras/projetos"""
    
    class StatusChoices(models.TextChoices):
        PLANEJAMENTO = 'PLANEJAMENTO', 'Planejamento'
        LICITACAO = 'LICITACAO', 'Licitação'
        EXECUCAO = 'EXECUCAO', 'Em Execução'
        PARALISADA = 'PARALISADA', 'Paralisada'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    name = models.CharField(max_length=200, verbose_name='Nome da Obra')
    contract = models.ForeignKey(
        'licitacao.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_projects',
        verbose_name='Contrato'
    )
    location_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name='Latitude'
    )
    location_lng = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name='Longitude'
    )
    address = models.TextField(verbose_name='Endereço')
    budget = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Orçamento'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PLANEJAMENTO,
        verbose_name='Status'
    )
    start_date = models.DateField(verbose_name='Data de Início')
    expected_end_date = models.DateField(verbose_name='Data Prevista de Conclusão')
    actual_end_date = models.DateField(null=True, blank=True, verbose_name='Data Real de Conclusão')
    description = models.TextField(verbose_name='Descrição da Obra')
    responsible = models.CharField(max_length=200, verbose_name='Responsável')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Obra/Projeto'
        verbose_name_plural = 'Obras/Projetos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def progress_physical(self):
        """Retorna o progresso físico mais recente"""
        latest_progress = self.progress_set.order_by('-ref_month').first()
        return latest_progress.physical_pct if latest_progress else 0
    
    @property
    def progress_financial(self):
        """Retorna o progresso financeiro mais recente"""
        latest_progress = self.progress_set.order_by('-ref_month').first()
        return latest_progress.financial_pct if latest_progress else 0


class WorkProgress(models.Model):
    """Modelo para progresso mensal das obras"""
    
    project = models.ForeignKey(
        WorkProject,
        on_delete=models.CASCADE,
        related_name='progress_set',
        verbose_name='Projeto'
    )
    ref_month = models.DateField(verbose_name='Mês de Referência')
    physical_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name='Progresso Físico (%)'
    )
    financial_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name='Progresso Financeiro (%)'
    )
    notes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Progresso da Obra'
        verbose_name_plural = 'Progressos da Obra'
        ordering = ['project', '-ref_month']
        unique_together = ['project', 'ref_month']
    
    def __str__(self):
        return f"Progresso de {self.project.name} - {self.ref_month.strftime('%m/%Y')}"


class WorkPhoto(models.Model):
    """Modelo para fotos das obras"""
    
    project = models.ForeignKey(
        WorkProject,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Projeto'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descrição')
    photo = models.ImageField(
        upload_to='work_photos/',
        verbose_name='Foto'
    )
    taken_date = models.DateField(verbose_name='Data da Foto')
    location = models.CharField(max_length=200, blank=True, verbose_name='Localização')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Foto da Obra'
        verbose_name_plural = 'Fotos da Obra'
        ordering = ['project', '-taken_date']
    
    def __str__(self):
        return f"Foto: {self.title} - {self.project.name}"
