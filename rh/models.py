from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Employee(models.Model):
    """Modelo para funcionários"""
    
    class RegimeChoices(models.TextChoices):
        CLT = 'CLT', 'CLT'
        ESTATUTARIO = 'ESTATUTARIO', 'Estatutário'
        TEMPORARIO = 'TEMPORARIO', 'Temporário'
        TERCEIRIZADO = 'TERCEIRIZADO', 'Terceirizado'
    
    class StatusChoices(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'
        APOSENTADO = 'APOSENTADO', 'Aposentado'
        DEMITIDO = 'DEMITIDO', 'Demitido'
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='employee_profile',
        verbose_name='Usuário'
    )
    matricula = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='Matrícula'
    )
    cargo = models.CharField(max_length=100, verbose_name='Cargo')
    lotacao = models.CharField(max_length=100, verbose_name='Lotação')
    regime = models.CharField(
        max_length=20,
        choices=RegimeChoices.choices,
        default=RegimeChoices.CLT,
        verbose_name='Regime'
    )
    admissao_dt = models.DateField(verbose_name='Data de Admissão')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ATIVO,
        verbose_name='Status'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.matricula}"
    
    @property
    def nome_completo(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email


class VacationRequest(models.Model):
    """Modelo para solicitações de férias"""
    
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        APPROVED = 'APPROVED', 'Aprovado'
        REJECTED = 'REJECTED', 'Rejeitado'
        CANCELLED = 'CANCELLED', 'Cancelado'
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='vacation_requests',
        verbose_name='Funcionário'
    )
    period_start = models.DateField(verbose_name='Início do Período')
    period_end = models.DateField(verbose_name='Fim do Período')
    days_requested = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name='Dias Solicitados'
    )
    reason = models.TextField(blank=True, verbose_name='Justificativa')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name='Status'
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_vacations',
        verbose_name='Aprovador'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Aprovado em')
    rejection_reason = models.TextField(blank=True, verbose_name='Motivo da Rejeição')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Solicitação de Férias'
        verbose_name_plural = 'Solicitações de Férias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Férias de {self.employee.nome_completo} - {self.get_status_display()}"


class Payslip(models.Model):
    """Modelo para contracheques"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name='Funcionário'
    )
    competencia = models.DateField(verbose_name='Competência')
    bruto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Valor Bruto'
    )
    descontos = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Descontos'
    )
    liquido = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Valor Líquido'
    )
    pdf_url = models.URLField(blank=True, null=True, verbose_name='URL do PDF')
    pdf_file = models.FileField(
        upload_to='payslips/',
        blank=True,
        null=True,
        verbose_name='Arquivo PDF'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Contracheque'
        verbose_name_plural = 'Contracheques'
        ordering = ['-competencia', 'employee__user__first_name']
        unique_together = ['employee', 'competencia']
    
    def __str__(self):
        return f"Contracheque de {self.employee.nome_completo} - {self.competencia.strftime('%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Calcula o valor líquido automaticamente
        if not self.liquido:
            self.liquido = self.bruto - self.descontos
        super().save(*args, **kwargs)
