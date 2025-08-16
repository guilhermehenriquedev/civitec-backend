from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
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
        
        # MASTER_ADMIN vê todos os contracheques
        if user.is_master_admin:
            return Payslip.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR veem contracheques do RH
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'RH':
                return Payslip.objects.all()
            return Payslip.objects.none()
        
        # EMPLOYEE vê apenas seus próprios contracheques
        if user.is_employee:
            return Payslip.objects.filter(employee__user=user)
        
        return Payslip.objects.none()
    
    @action(detail=True, methods=['get'], permission_classes=[IsEmployeeSelf])
    def download(self, request, pk=None):
        """Endpoint para download do contracheque"""
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
        
        # Aqui você implementaria a lógica de download
        # Por enquanto, retornamos apenas as informações
        return Response({
            'message': 'Download iniciado',
            'payslip_id': payslip.id,
            'employee': payslip.employee.nome_completo,
            'competencia': payslip.competencia,
        })
