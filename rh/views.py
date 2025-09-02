from django.shortcuts import render
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
import io

# Import condicional do ReportLab para não quebrar o sistema
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab não disponível. Funcionalidade de PDF será limitada.")

from .models import Employee, VacationRequest, Payslip
from .serializers import EmployeeSerializer, VacationRequestSerializer, PayslipSerializer
from users.permissions import IsMasterAdmin, IsSectorAdmin, IsSectorOperator, IsEmployeeSelf


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para funcionários"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'RH'
    
    def get_queryset(self):
        user = self.request.user
        
        # MASTER_ADMIN vê todos os funcionários
        if user.is_master_admin:
            return Employee.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem apenas funcionários do RH
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'RH':
                return Employee.objects.all()
            return Employee.objects.none()
        
        # EMPLOYEE vê apenas seu próprio perfil
        if user.is_employee:
            return Employee.objects.filter(user=user)
        
        return Employee.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[IsEmployeeSelf])
    def my_profile(self, request):
        """Retorna o perfil do funcionário logado"""
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Perfil de funcionário não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class VacationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet para solicitações de férias"""
    queryset = VacationRequest.objects.all()
    serializer_class = VacationRequestSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'RH'
    
    def get_queryset(self):
        user = self.request.user
        
        # MASTER_ADMIN vê todas as solicitações
        if user.is_master_admin:
            return VacationRequest.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem solicitações do RH
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'RH':
                return VacationRequest.objects.all()
            return VacationRequest.objects.none()
        
        # EMPLOYEE vê apenas suas próprias solicitações
        if user.is_employee:
            return VacationRequest.objects.filter(employee__user=user)
        
        return VacationRequest.objects.none()
    
    def perform_create(self, serializer):
        """Cria uma solicitação de férias"""
        user = self.request.user
        
        if user.is_employee:
            # EMPLOYEE só pode criar solicitação para si mesmo
            try:
                employee = Employee.objects.get(user=user)
                serializer.save(employee=employee)
            except Employee.DoesNotExist:
                raise serializers.ValidationError("Perfil de funcionário não encontrado")
        else:
            # ADMIN pode criar para qualquer funcionário
            serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsSectorAdmin])
    def approve(self, request, pk=None):
        """Aprova uma solicitação de férias"""
        vacation_request = self.get_object()
        user = request.user
        
        # Apenas RH ADMIN pode aprovar
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'RH')):
            return Response(
                {'error': 'Sem permissão para aprovar solicitações'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        vacation_request.status = VacationRequest.StatusChoices.APPROVED
        vacation_request.approver = user
        vacation_request.approved_at = timezone.now()
        vacation_request.save()
        
        serializer = self.get_serializer(vacation_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSectorAdmin])
    def reject(self, request, pk=None):
        """Rejeita uma solicitação de férias"""
        vacation_request = self.get_object()
        user = request.user
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Apenas RH ADMIN pode rejeitar
        if not (user.is_master_admin or (user.is_sector_admin and user.sector == 'RH')):
            return Response(
                {'error': 'Sem permissão para rejeitar solicitações'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        vacation_request.status = VacationRequest.StatusChoices.REJECTED
        vacation_request.approver = user
        vacation_request.approved_at = timezone.now()
        vacation_request.rejection_reason = rejection_reason
        vacation_request.save()
        
        serializer = self.get_serializer(vacation_request)
        return Response(serializer.data)


class PayslipViewSet(viewsets.ModelViewSet):
    """ViewSet para contracheques"""
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'RH'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Payslip.objects.none()
        
        # MASTER_ADMIN vê todos os contracheques
        if user.is_master_admin:
            queryset = Payslip.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem contracheques do RH
        elif user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'RH':
                queryset = Payslip.objects.all()
        
        # EMPLOYEE vê apenas seus próprios contracheques
        elif user.is_employee:
            queryset = Payslip.objects.filter(employee__user=user)
        
        # Aplicar filtros de query string
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            try:
                queryset = queryset.filter(employee_id=int(employee_id))
            except (ValueError, TypeError):
                pass  # Ignora valores inválidos
        
        competencia = self.request.query_params.get('competencia')
        if competencia:
            try:
                # Espera formato YYYY-MM
                queryset = queryset.filter(competencia__icontains=competencia)
            except (ValueError, TypeError):
                pass
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(employee__user__first_name__icontains=search) |
                models.Q(employee__user__last_name__icontains=search) |
                models.Q(employee__matricula__icontains=search) |
                models.Q(competencia__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[IsEmployeeSelf])
    def download(self, request, pk=None):
        """Endpoint para download do contracheque em PDF"""
        payslip = self.get_object()
        
        # Verificar se o usuário tem acesso ao contracheque
        user = request.user
        if not (user.is_master_admin or 
                (user.is_sector_admin and user.sector == 'RH') or
                (user.is_employee and payslip.employee.user == user)):
            return Response(
                {'error': 'Sem permissão para acessar este contracheque'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            if REPORTLAB_AVAILABLE:
                # Gerar PDF do contracheque usando ReportLab
                pdf_buffer = self.generate_payslip_pdf(payslip)
                
                # Configurar resposta HTTP para download
                filename = f"contracheque-{payslip.competencia}-{payslip.employee.matricula}.pdf"
                
                response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = len(pdf_buffer.getvalue())
                
                # Headers CORS para permitir download
                response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length'
                
                return response
            else:
                # Fallback: retornar dados em formato JSON com instruções
                return Response({
                    'message': 'Funcionalidade de PDF não disponível',
                    'instruction': 'Instale o ReportLab: pip install reportlab',
                    'payslip_data': {
                        'id': payslip.id,
                        'employee': payslip.employee.nome_completo,
                        'matricula': payslip.employee.matricula,
                        'competencia': payslip.competencia,
                        'bruto': payslip.bruto,
                        'descontos': payslip.descontos,
                        'liquido': payslip.liquido,
                        'created_at': payslip.created_at,
                    }
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
            
        except Exception as e:
            return Response(
                {'error': f'Erro ao gerar PDF: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generate_payslip_pdf(self, payslip):
        """Gera PDF do contracheque usando ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab não está disponível. Instale com: pip install reportlab")
        
        buffer = io.BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo para título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Estilo para cabeçalho
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Título principal
        title = Paragraph("CONTRACHEQUE", title_style)
        story.append(title)
        
        # Informações da empresa
        company_info = Paragraph("PREFEITURA MUNICIPAL", header_style)
        story.append(company_info)
        
        # Espaçador
        story.append(Spacer(1, 20))
        
        # Informações do funcionário
        employee_data = [
            ['Funcionário:', payslip.employee.nome_completo],
            ['Matrícula:', payslip.employee.matricula],
            ['Cargo:', payslip.employee.cargo],
            ['Lotação:', payslip.employee.lotacao],
            ['Competência:', payslip.competencia],
        ]
        
        employee_table = Table(employee_data, colWidths=[2*inch, 4*inch])
        employee_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(employee_table)
        story.append(Spacer(1, 20))
        
        # Valores financeiros
        financial_data = [
            ['Descrição', 'Valor (R$)', 'Tipo'],
            ['Salário Bruto', f"{payslip.bruto:,.2f}", 'Proventos'],
            ['Descontos', f"{payslip.descontos:,.2f}", 'Descontos'],
            ['', '', ''],
            ['SALÁRIO LÍQUIDO', f"{payslip.liquido:,.2f}", 'Total'],
        ]
        
        financial_table = Table(financial_data, colWidths=[3*inch, 2*inch, 1*inch])
        financial_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightblue),
            ('TEXTCOLOR', (0, 4), (-1, 4), colors.darkblue),
        ]))
        
        story.append(financial_table)
        story.append(Spacer(1, 30))
        
        # Rodapé
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        footer = Paragraph(
            f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}",
            footer_style
        )
        story.append(footer)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
