from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Taxpayer(models.Model):
    """Modelo para contribuintes"""
    
    class TypeChoices(models.TextChoices):
        PF = 'PF', 'Pessoa Física'
        PJ = 'PJ', 'Pessoa Jurídica'
    
    name = models.CharField(max_length=200, verbose_name='Nome/Razão Social')
    doc = models.CharField(max_length=18, unique=True, verbose_name='CPF/CNPJ')
    type = models.CharField(
        max_length=2,
        choices=TypeChoices.choices,
        default=TypeChoices.PF,
        verbose_name='Tipo'
    )
    address = models.TextField(verbose_name='Endereço')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Contribuinte'
        verbose_name_plural = 'Contribuintes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Invoice(models.Model):
    """Modelo para notas fiscais"""
    
    class StatusChoices(models.TextChoices):
        EMITIDA = 'EMITIDA', 'Emitida'
        CANCELADA = 'CANCELADA', 'Cancelada'
        PAGA = 'PAGA', 'Paga'
    
    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Contribuinte'
    )
    number = models.CharField(max_length=20, unique=True, verbose_name='Número da NF')
    issue_dt = models.DateField(verbose_name='Data de Emissão')
    service_code = models.CharField(max_length=10, verbose_name='Código do Serviço')
    description = models.TextField(verbose_name='Descrição do Serviço')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.EMITIDA,
        verbose_name='Status'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        ordering = ['-issue_dt', 'number']
    
    def __str__(self):
        return f"NF {self.number} - {self.taxpayer.name}"


class Assessment(models.Model):
    """Modelo para avaliações/guias de impostos"""
    
    class TaxKindChoices(models.TextChoices):
        ISS = 'ISS', 'ISS'
        IPTU = 'IPTU', 'IPTU'
        ITBI = 'ITBI', 'ITBI'
        OUTROS = 'OUTROS', 'Outros'
    
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EMITIDA = 'EMITIDA', 'Emitida'
        PAGA = 'PAGA', 'Paga'
        VENCIDA = 'VENCIDA', 'Vencida'
    
    taxpayer = models.ForeignKey(
        Taxpayer,
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name='Contribuinte'
    )
    tax_kind = models.CharField(
        max_length=10,
        choices=TaxKindChoices.choices,
        verbose_name='Tipo de Imposto'
    )
    competence = models.DateField(verbose_name='Competência')
    principal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Principal'
    )
    multa = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Multa'
    )
    juros = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='Juros'
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Total'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        verbose_name='Status'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Avaliação/Guia'
        verbose_name_plural = 'Avaliações/Guias'
        ordering = ['-competence', 'taxpayer__name']
    
    def __str__(self):
        return f"{self.get_tax_kind_display()} - {self.taxpayer.name} ({self.competence.strftime('%m/%Y')})"
    
    def save(self, *args, **kwargs):
        # Calcula o total automaticamente
        if not self.total:
            self.total = self.principal + self.multa + self.juros
        super().save(*args, **kwargs)


class Billing(models.Model):
    """Modelo para cobranças/boletos"""
    
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PAGO = 'PAGO', 'Pago'
        VENCIDO = 'VENCIDO', 'Vencido'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name='billing',
        verbose_name='Avaliação'
    )
    due_dt = models.DateField(verbose_name='Data de Vencimento')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='Código de Barras')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Valor a Pagar'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        verbose_name='Status'
    )
    payment_dt = models.DateTimeField(null=True, blank=True, verbose_name='Data do Pagamento')
    payment_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='Valor Pago'
    )
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Cobrança'
        verbose_name_plural = 'Cobranças'
        ordering = ['due_dt', 'assessment__taxpayer__name']
    
    def __str__(self):
        return f"Boleto {self.barcode} - {self.assessment.taxpayer.name}"
    
    def save(self, *args, **kwargs):
        # Se não foi definido o valor, usa o total da avaliação
        if not self.amount:
            self.amount = self.assessment.total
        super().save(*args, **kwargs)
