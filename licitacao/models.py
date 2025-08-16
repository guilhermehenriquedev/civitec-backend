from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Procurement(models.Model):
    """Modelo para processos de licitação"""
    
    class ModalidadeChoices(models.TextChoices):
        CONCORRENCIA = 'CONCORRENCIA', 'Concorrência'
        PREGAO = 'PREGAO', 'Pregão'
        CONCURSO = 'CONCURSO', 'Concurso'
        LEILAO = 'LEILAO', 'Leilão'
        TOMADA_PRECOS = 'TOMADA_PRECOS', 'Tomada de Preços'
        CONVITE = 'CONVITE', 'Convite'
        OUTROS = 'OUTROS', 'Outros'
    
    class StatusChoices(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        ABERTA = 'ABERTA', 'Aberta'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        SUSPENSA = 'SUSPENSA', 'Suspensa'
        ENCERRADA = 'ENCERRADA', 'Encerrada'
        ANULADA = 'ANULADA', 'Anulada'
        HOMOLOGADA = 'HOMOLOGADA', 'Homologada'
    
    modalidade = models.CharField(
        max_length=20,
        choices=ModalidadeChoices.choices,
        verbose_name='Modalidade'
    )
    objeto = models.TextField(verbose_name='Objeto da Licitação')
    numero_processo = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Número do Processo'
    )
    valor_estimado = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Estimado'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RASCUNHO,
        verbose_name='Status'
    )
    data_abertura = models.DateField(verbose_name='Data de Abertura')
    data_encerramento = models.DateField(verbose_name='Data de Encerramento')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Processo de Licitação'
        verbose_name_plural = 'Processos de Licitação'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_modalidade_display()} - {self.numero_processo}"


class ProcPhase(models.Model):
    """Modelo para fases do processo de licitação"""
    
    class PhaseChoices(models.TextChoices):
        PUBLICACAO = 'PUBLICACAO', 'Publicação'
        INSCRICAO = 'INSCRICAO', 'Inscrição'
        HABILITACAO = 'HABILITACAO', 'Habilitação'
        PROPOSTAS = 'PROPOSTAS', 'Propostas'
        ABERTURA = 'ABERTURA', 'Abertura'
        JULGAMENTO = 'JULGAMENTO', 'Julgamento'
        HOMOLOGACAO = 'HOMOLOGACAO', 'Homologação'
        ADJUDICACAO = 'ADJUDICACAO', 'Adjudicação'
    
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    procurement = models.ForeignKey(
        Procurement,
        on_delete=models.CASCADE,
        related_name='phases',
        verbose_name='Processo'
    )
    fase = models.CharField(
        max_length=20,
        choices=PhaseChoices.choices,
        verbose_name='Fase'
    )
    start_dt = models.DateTimeField(verbose_name='Data de Início')
    end_dt = models.DateTimeField(verbose_name='Data de Fim')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Fase do Processo'
        verbose_name_plural = 'Fases do Processo'
        ordering = ['procurement', 'start_dt']
        unique_together = ['procurement', 'fase']
    
    def __str__(self):
        return f"{self.procurement.numero_processo} - {self.get_fase_display()}"


class Proposal(models.Model):
    """Modelo para propostas"""
    
    class StatusChoices(models.TextChoices):
        RECEBIDA = 'RECEBIDA', 'Recebida'
        HABILITADA = 'HABILITADA', 'Habilitada'
        DESABILITADA = 'DESABILITADA', 'Desabilitada'
        CLASSIFICADA = 'CLASSIFICADA', 'Classificada'
        DESCLASSIFICADA = 'DESCLASSIFICADA', 'Desclassificada'
    
    procurement = models.ForeignKey(
        Procurement,
        on_delete=models.CASCADE,
        related_name='proposals',
        verbose_name='Processo'
    )
    supplier_name = models.CharField(max_length=200, verbose_name='Nome do Fornecedor')
    supplier_doc = models.CharField(max_length=18, verbose_name='CPF/CNPJ do Fornecedor')
    valor = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor da Proposta'
    )
    classificacao = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='Classificação'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RECEBIDA,
        verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['procurement', 'classificacao', 'valor']
        unique_together = ['procurement', 'supplier_doc']
    
    def __str__(self):
        return f"Proposta de {self.supplier_name} - {self.procurement.numero_processo}"


class Award(models.Model):
    """Modelo para adjudicação/homologação"""
    
    procurement = models.OneToOneField(
        Procurement,
        on_delete=models.CASCADE,
        related_name='award',
        verbose_name='Processo'
    )
    supplier = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='awards',
        verbose_name='Fornecedor Vencedor'
    )
    valor_adjudicado = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Adjudicado'
    )
    homolog_dt = models.DateTimeField(verbose_name='Data da Homologação')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Adjudicação'
        verbose_name_plural = 'Adjudicações'
        ordering = ['-homolog_dt']
    
    def __str__(self):
        return f"Adjudicação de {self.procurement.numero_processo}"


class Contract(models.Model):
    """Modelo para contratos"""
    
    class StatusChoices(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        ATIVO = 'ATIVO', 'Ativo'
        SUSPENSO = 'SUSPENSO', 'Suspenso'
        ENCERRADO = 'ENCERRADO', 'Encerrado'
        RESCINDIDO = 'RESCINDIDO', 'Rescindido'
    
    procurement = models.ForeignKey(
        Procurement,
        on_delete=models.CASCADE,
        related_name='contracts',
        null=True,
        blank=True,
        verbose_name='Processo de Licitação'
    )
    number = models.CharField(max_length=50, unique=True, verbose_name='Número do Contrato')
    supplier_name = models.CharField(max_length=200, verbose_name='Nome do Fornecedor')
    supplier_doc = models.CharField(max_length=18, verbose_name='CPF/CNPJ do Fornecedor')
    start_dt = models.DateField(verbose_name='Data de Início')
    end_dt = models.DateField(verbose_name='Data de Fim')
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor Total'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RASCUNHO,
        verbose_name='Status'
    )
    objeto = models.TextField(verbose_name='Objeto do Contrato')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Contrato {self.number} - {self.supplier_name}"


class ContractMilestone(models.Model):
    """Modelo para marcos do contrato"""
    
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        ATRASADO = 'ATRASADO', 'Atrasado'
    
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name='Contrato'
    )
    desc = models.CharField(max_length=200, verbose_name='Descrição')
    due_dt = models.DateField(verbose_name='Data de Vencimento')
    valor = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor do Marco'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        verbose_name='Status'
    )
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    # Campos de auditoria
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Marco do Contrato'
        verbose_name_plural = 'Marcos do Contrato'
        ordering = ['contract', 'due_dt']
    
    def __str__(self):
        return f"Marco: {self.desc} - {self.contract.number}"
