from rest_framework import serializers
from .models import Employee, VacationRequest, Payslip
from users.serializers import UserSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer para funcionários"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    nome_completo = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'matricula', 'cargo', 'lotacao', 'regime',
            'admissao_dt', 'status', 'nome_completo', 'email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_matricula(self, value):
        """Valida se a matrícula é única"""
        if Employee.objects.filter(matricula=value).exists():
            raise serializers.ValidationError("Esta matrícula já está em uso.")
        return value


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de funcionários"""
    user_id = serializers.IntegerField()
    
    class Meta:
        model = Employee
        fields = [
            'user_id', 'matricula', 'cargo', 'lotacao', 'regime',
            'admissao_dt', 'status'
        ]
    
    def validate_user_id(self, value):
        """Valida se o usuário existe e não é funcionário"""
        from users.models import User
        try:
            user = User.objects.get(id=value)
            if hasattr(user, 'employee_profile'):
                raise serializers.ValidationError("Este usuário já possui perfil de funcionário.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")
        return value


class VacationRequestSerializer(serializers.ModelSerializer):
    """Serializer para solicitações de férias"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    approver = UserSerializer(read_only=True)
    
    class Meta:
        model = VacationRequest
        fields = [
            'id', 'employee', 'employee_id', 'period_start', 'period_end', 'days_requested',
            'reason', 'status', 'approver', 'approved_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'approver', 'approved_at', 'rejection_reason', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validações customizadas"""
        period_start = attrs.get('period_start')
        period_end = attrs.get('period_end')
        days_requested = attrs.get('days_requested')
        
        if period_start and period_end:
            if period_start >= period_end:
                raise serializers.ValidationError("A data de início deve ser anterior à data de fim.")
            
            # Calcular dias entre as datas
            delta = period_end - period_start
            if delta.days != days_requested:
                raise serializers.ValidationError("O número de dias deve corresponder ao período solicitado.")
        
        if days_requested and (days_requested < 1 or days_requested > 30):
            raise serializers.ValidationError("O número de dias deve estar entre 1 e 30.")
        
        return attrs


class VacationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de solicitações de férias"""
    employee_id = serializers.IntegerField()
    
    class Meta:
        model = VacationRequest
        fields = [
            'employee_id', 'period_start', 'period_end', 'days_requested', 'reason'
        ]
    
    def validate_employee_id(self, value):
        """Valida se o funcionário existe"""
        from .models import Employee
        try:
            Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Funcionário não encontrado.")
        return value


class PayslipSerializer(serializers.ModelSerializer):
    """Serializer para contracheques"""
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'employee', 'employee_id', 'competencia', 'bruto', 'descontos',
            'liquido', 'pdf_url', 'pdf_file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'liquido', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validações customizadas"""
        bruto = attrs.get('bruto', 0)
        descontos = attrs.get('descontos', 0)
        
        if bruto < descontos:
            raise serializers.ValidationError("Os descontos não podem ser maiores que o valor bruto.")
        
        return attrs


class PayslipCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de contracheques"""
    employee_id = serializers.IntegerField()
    
    class Meta:
        model = Payslip
        fields = [
            'employee_id', 'competencia', 'bruto', 'descontos', 'pdf_url', 'pdf_file'
        ]
    
    def validate_employee_id(self, value):
        """Valida se o funcionário existe"""
        from .models import Employee
        try:
            Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Funcionário não encontrado.")
        return value
