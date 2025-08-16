from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from users.permissions import IsMasterAdmin, IsSectorAdmin


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet para dashboards e relatórios"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def master_dashboard(self, request):
        """Dashboard master com visão geral de todos os setores"""
        if not request.user.is_master_admin:
            return Response({'error': 'Acesso negado'}, status=403)
        
        # Dados de RH
        try:
            from rh.models import Employee, VacationRequest, Payslip
            rh_data = {
                'total_employees': Employee.objects.filter(status='ATIVO').count(),
                'pending_vacations': VacationRequest.objects.filter(status='PENDING').count(),
                'total_payslips': Payslip.objects.count(),
            }
        except ImportError:
            rh_data = {'error': 'Módulo RH não disponível'}
        
        # Dados de Tributos
        try:
            from tributos.models import Taxpayer, Assessment, Billing
            tributos_data = {
                'total_taxpayers': Taxpayer.objects.filter(is_active=True).count(),
                'pending_assessments': Assessment.objects.filter(status='PENDENTE').count(),
                'total_billings': Billing.objects.count(),
                'monthly_revenue': Billing.objects.filter(
                    status='PAGO',
                    payment_dt__month=timezone.now().month
                ).aggregate(total=Sum('amount'))['total'] or 0,
            }
        except ImportError:
            tributos_data = {'error': 'Módulo Tributos não disponível'}
        
        # Dados de Licitação
        try:
            from licitacao.models import Procurement, Proposal, Contract
            licitacao_data = {
                'active_procurements': Procurement.objects.filter(status='EM_ANDAMENTO').count(),
                'total_proposals': Proposal.objects.count(),
                'active_contracts': Contract.objects.filter(status='ATIVO').count(),
            }
        except ImportError:
            licitacao_data = {'error': 'Módulo Licitação não disponível'}
        
        # Dados de Obras
        try:
            from obras.models import WorkProject, WorkProgress
            obras_data = {
                'total_projects': WorkProject.objects.count(),
                'active_projects': WorkProject.objects.filter(status='EXECUCAO').count(),
                'avg_progress': WorkProgress.objects.aggregate(avg=Avg('physical_pct'))['avg'] or 0,
            }
        except ImportError:
            obras_data = {'error': 'Módulo Obras não disponível'}
        
        return Response({
            'rh': rh_data,
            'tributos': tributos_data,
            'licitacao': licitacao_data,
            'obras': obras_data,
            'generated_at': timezone.now(),
        })
    
    @action(detail=False, methods=['get'])
    def sector_dashboard(self, request, sector):
        """Dashboard específico para um setor"""
        user = request.user
        
        # Verificar permissões
        if not (user.is_master_admin or 
                (user.is_sector_admin and user.sector == sector) or
                (user.is_sector_operator and user.sector == sector)):
            return Response({'error': 'Acesso negado'}, status=403)
        
        if sector == 'RH':
            return self._get_rh_dashboard()
        elif sector == 'TRIBUTOS':
            return self._get_tributos_dashboard()
        elif sector == 'LICITACAO':
            return self._get_licitacao_dashboard()
        elif sector == 'OBRAS':
            return self._get_obras_dashboard()
        else:
            return Response({'error': 'Setor inválido'}, status=400)
    
    def _get_rh_dashboard(self):
        """Dashboard específico do RH"""
        try:
            from rh.models import Employee, VacationRequest, Payslip
            from django.db.models import Q
            
            current_month = timezone.now().month
            current_year = timezone.now().year
            
            data = {
                'employees': {
                    'total': Employee.objects.count(),
                    'active': Employee.objects.filter(status='ATIVO').count(),
                    'inactive': Employee.objects.filter(status='INATIVO').count(),
                },
                'vacations': {
                    'pending': VacationRequest.objects.filter(status='PENDING').count(),
                    'approved': VacationRequest.objects.filter(status='APPROVED').count(),
                    'rejected': VacationRequest.objects.filter(status='REJECTED').count(),
                },
                'payslips': {
                    'current_month': Payslip.objects.filter(
                        competencia__month=current_month,
                        competencia__year=current_year
                    ).count(),
                    'total_year': Payslip.objects.filter(
                        competencia__year=current_year
                    ).count(),
                }
            }
            return Response(data)
        except ImportError:
            return Response({'error': 'Módulo RH não disponível'}, status=500)
    
    def _get_tributos_dashboard(self):
        """Dashboard específico de Tributos"""
        try:
            from tributos.models import Taxpayer, Assessment, Billing
            from django.db.models import Sum
            
            current_month = timezone.now().month
            current_year = timezone.now().year
            
            data = {
                'taxpayers': {
                    'total': Taxpayer.objects.filter(is_active=True).count(),
                    'pf': Taxpayer.objects.filter(type='PF', is_active=True).count(),
                    'pj': Taxpayer.objects.filter(type='PJ', is_active=True).count(),
                },
                'assessments': {
                    'pending': Assessment.objects.filter(status='PENDENTE').count(),
                    'emitted': Assessment.objects.filter(status='EMITIDA').count(),
                    'paid': Assessment.objects.filter(status='PAGA').count(),
                },
                'revenue': {
                    'current_month': Billing.objects.filter(
                        status='PAGO',
                        payment_dt__month=current_month,
                        payment_dt__year=current_year
                    ).aggregate(total=Sum('amount'))['total'] or 0,
                    'current_year': Billing.objects.filter(
                        status='PAGO',
                        payment_dt__year=current_year
                    ).aggregate(total=Sum('amount'))['total'] or 0,
                }
            }
            return Response(data)
        except ImportError:
            return Response({'error': 'Módulo Tributos não disponível'}, status=500)
    
    def _get_licitacao_dashboard(self):
        """Dashboard específico de Licitação"""
        try:
            from licitacao.models import Procurement, Proposal, Contract
            from django.db.models import Sum
            
            data = {
                'procurements': {
                    'total': Procurement.objects.count(),
                    'draft': Procurement.objects.filter(status='RASCUNHO').count(),
                    'open': Procurement.objects.filter(status='ABERTA').count(),
                    'in_progress': Procurement.objects.filter(status='EM_ANDAMENTO').count(),
                    'closed': Procurement.objects.filter(status='ENCERRADA').count(),
                },
                'proposals': {
                    'total': Proposal.objects.count(),
                    'received': Proposal.objects.filter(status='RECEBIDA').count(),
                    'classified': Proposal.objects.filter(status='CLASSIFICADA').count(),
                },
                'contracts': {
                    'total': Contract.objects.count(),
                    'active': Contract.objects.filter(status='ATIVO').count(),
                    'draft': Contract.objects.filter(status='RASCUNHO').count(),
                    'closed': Contract.objects.filter(status='ENCERRADO').count(),
                }
            }
            return Response(data)
        except ImportError:
            return Response({'error': 'Módulo Licitação não disponível'}, status=500)
    
    def _get_obras_dashboard(self):
        """Dashboard específico de Obras"""
        try:
            from obras.models import WorkProject, WorkProgress
            from django.db.models import Avg, Sum
            
            data = {
                'projects': {
                    'total': WorkProject.objects.count(),
                    'planning': WorkProject.objects.filter(status='PLANEJAMENTO').count(),
                    'execution': WorkProject.objects.filter(status='EXECUCAO').count(),
                    'completed': WorkProject.objects.filter(status='CONCLUIDA').count(),
                    'cancelled': WorkProject.objects.filter(status='CANCELADA').count(),
                },
                'progress': {
                    'avg_physical': WorkProgress.objects.aggregate(avg=Avg('physical_pct'))['avg'] or 0,
                    'avg_financial': WorkProgress.objects.aggregate(avg=Avg('financial_pct'))['avg'] or 0,
                },
                'budget': {
                    'total_budget': WorkProject.objects.aggregate(total=Sum('budget'))['total'] or 0,
                    'executed_budget': WorkProject.objects.filter(status='EXECUCAO').aggregate(total=Sum('budget'))['total'] or 0,
                }
            }
            return Response(data)
        except ImportError:
            return Response({'error': 'Módulo Obras não disponível'}, status=500)
