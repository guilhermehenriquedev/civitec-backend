from django.shortcuts import render
from django.db import models
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Taxpayer, Invoice, Assessment, Billing
from .serializers import TaxpayerSerializer, InvoiceSerializer, AssessmentSerializer, BillingSerializer
from users.permissions import IsSectorAdmin, IsSectorOperator
import io
import os


# Create your views here.


class TaxpayerViewSet(viewsets.ModelViewSet):
    """ViewSet para contribuintes"""
    queryset = Taxpayer.objects.all()
    serializer_class = TaxpayerSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Taxpayer.objects.none()
        
        # MASTER_ADMIN vê todos os contribuintes
        if user.is_master_admin:
            queryset = Taxpayer.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem contribuintes do TRIBUTOS
        elif user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'TRIBUTOS':
                queryset = Taxpayer.objects.all()
        
        # Aplicar filtros de query string
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(doc__icontains=search)
            )
        
        doc_type = self.request.query_params.get('type')
        if doc_type:
            queryset = queryset.filter(type=doc_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas dos contribuintes"""
        user = self.request.user
        
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'TRIBUTOS')):
            return Response({'error': 'Sem permissão'}, status=status.HTTP_403_FORBIDDEN)
        
        total = Taxpayer.objects.count()
        ativos = Taxpayer.objects.filter(is_active=True).count()
        pf = Taxpayer.objects.filter(type='PF').count()
        pj = Taxpayer.objects.filter(type='PJ').count()
        
        return Response({
            'total': total,
            'ativos': ativos,
            'pessoa_fisica': pf,
            'pessoa_juridica': pj
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet para notas fiscais"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.none()
        
        # MASTER_ADMIN vê todas as notas fiscais
        if user.is_master_admin:
            queryset = Invoice.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem notas fiscais do TRIBUTOS
        elif user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'TRIBUTOS':
                queryset = Invoice.objects.all()
        
        # Aplicar filtros de query string
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(number__icontains=search) |
                models.Q(taxpayer__name__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        taxpayer_id = self.request.query_params.get('taxpayer_id')
        if taxpayer_id:
            try:
                queryset = queryset.filter(taxpayer_id=int(taxpayer_id))
            except (ValueError, TypeError):
                pass
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                queryset = queryset.filter(issue_dt__gte=start_date)
            except (ValueError, TypeError):
                pass
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                queryset = queryset.filter(issue_dt__lte=end_date)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das notas fiscais"""
        user = self.request.user
        
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'TRIBUTOS')):
            return Response({'error': 'Sem permissão'}, status=status.HTTP_403_FORBIDDEN)
        
        total = Invoice.objects.count()
        emitidas = Invoice.objects.filter(status='EMITIDA').count()
        canceladas = Invoice.objects.filter(status='CANCELADA').count()
        pagas = Invoice.objects.filter(status='PAGA').count()
        total_value = Invoice.objects.filter(status='EMITIDA').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return Response({
            'total': total,
            'emitidas': emitidas,
            'canceladas': canceladas,
            'pagas': pagas,
            'total_value': float(total_value)
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela uma nota fiscal"""
        invoice = self.get_object()
        reason = request.data.get('reason', '')
        
        if invoice.status != 'EMITIDA':
            return Response(
                {'error': 'Apenas notas emitidas podem ser canceladas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'CANCELADA'
        invoice.save()
        
        # TODO: Criar log de auditoria
        return Response({'message': 'Nota fiscal cancelada com sucesso'})
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download da nota fiscal em PDF"""
        invoice = self.get_object()
        
        # TODO: Implementar geração de PDF
        # Por enquanto, retorna dados em JSON
        return Response({
            'message': 'PDF da nota fiscal',
            'invoice_data': {
                'number': invoice.number,
                'taxpayer': invoice.taxpayer.name,
                'amount': float(invoice.amount),
                'status': invoice.status
            }
        })
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Valida uma nota fiscal por número e código"""
        number = request.data.get('number')
        code = request.data.get('code')
        
        if not number or not code:
            return Response(
                {'error': 'Número e código são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invoice = Invoice.objects.get(number=number)
            # TODO: Implementar validação por código/QR
            is_valid = True  # Placeholder
            
            return Response({
                'is_valid': is_valid,
                'invoice': {
                    'number': invoice.number,
                    'taxpayer': invoice.taxpayer.name,
                    'amount': float(invoice.amount),
                    'status': invoice.status,
                    'issue_dt': invoice.issue_dt
                }
            })
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Nota fiscal não encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet para avaliações/guias"""
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Assessment.objects.none()
        
        # MASTER_ADMIN vê todas as avaliações
        if user.is_master_admin:
            queryset = Assessment.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem avaliações do TRIBUTOS
        elif user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'TRIBUTOS':
                queryset = Assessment.objects.all()
        
        # Aplicar filtros de query string
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(taxpayer__name__icontains=search) |
                models.Q(tax_kind__icontains=search)
            )
        
        taxpayer_id = self.request.query_params.get('taxpayer_id')
        if taxpayer_id:
            try:
                queryset = queryset.filter(taxpayer_id=int(taxpayer_id))
            except (ValueError, TypeError):
                pass
        
        tax_kind = self.request.query_params.get('tax_kind')
        if tax_kind:
            queryset = queryset.filter(tax_kind=tax_kind)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        competence = self.request.query_params.get('competence')
        if competence:
            try:
                queryset = queryset.filter(competence__icontains=competence)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das avaliações"""
        user = self.request.user
        
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'TRIBUTOS')):
            return Response({'error': 'Sem permissão'}, status=status.HTTP_403_FORBIDDEN)
        
        total = Assessment.objects.count()
        pendentes = Assessment.objects.filter(status='PENDENTE').count()
        emitidas = Assessment.objects.filter(status='EMITIDA').count()
        pagas = Assessment.objects.filter(status='PAGA').count()
        vencidas = Assessment.objects.filter(status='VENCIDA').count()
        
        total_value = Assessment.objects.filter(status__in=['PENDENTE', 'EMITIDA']).aggregate(
            total=models.Sum('total')
        )['total'] or 0
        
        return Response({
            'total': total,
            'pendentes': pendentes,
            'emitidas': emitidas,
            'pagas': pagas,
            'vencidas': vencidas,
            'total_value': float(total_value)
        })
    
    @action(detail=True, methods=['post'])
    def generate_code(self, request, pk=None):
        """Gera código de arrecadação para uma avaliação"""
        assessment = self.get_object()
        
        # Gerar código único de arrecadação
        import uuid
        code = f"DAM-{assessment.tax_kind}-{assessment.competence.strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Criar ou atualizar cobrança
        billing, created = Billing.objects.get_or_create(
            assessment=assessment,
            defaults={
                'due_dt': timezone.now().date(),
                'barcode': code,
                'amount': assessment.total
            }
        )
        
        if not created:
            billing.barcode = code
            billing.amount = assessment.total
            billing.save()
        
        return Response({
            'code': code,
            'billing_id': billing.id,
            'due_dt': billing.due_dt,
            'amount': float(billing.amount)
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download da guia de arrecadação em PDF"""
        assessment = self.get_object()
        
        # TODO: Implementar geração de PDF
        # Por enquanto, retorna dados em JSON
        return Response({
            'message': 'PDF da guia de arrecadação',
            'assessment_data': {
                'tax_kind': assessment.tax_kind,
                'taxpayer': assessment.taxpayer.name,
                'competence': assessment.competence,
                'total': float(assessment.total)
            }
        })


class BillingViewSet(viewsets.ModelViewSet):
    """ViewSet para cobranças"""
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Billing.objects.none()
        
        # MASTER_ADMIN vê todas as cobranças
        if user.is_master_admin:
            queryset = Billing.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem cobranças do TRIBUTOS
        elif user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'TRIBUTOS':
                queryset = Billing.objects.all()
        
        # Aplicar filtros de query string
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                queryset = queryset.filter(due_dt__gte=start_date)
            except (ValueError, TypeError):
                pass
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                queryset = queryset.filter(due_dt__lte=end_date)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das cobranças"""
        user = self.request.user
        
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'TRIBUTOS')):
            return Response({'error': 'Sem permissão'}, status=status.HTTP_403_FORBIDDEN)
        
        total = Billing.objects.count()
        pendentes = Billing.objects.filter(status='PENDENTE').count()
        pagos = Billing.objects.filter(status='PAGO').count()
        vencidos = Billing.objects.filter(status='VENCIDO').count()
        
        total_value = Billing.objects.filter(status='PENDENTE').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return Response({
            'total': total,
            'pendentes': pendentes,
            'pagos': pagos,
            'vencidos': vencidos,
            'total_value': float(total_value)
        })
