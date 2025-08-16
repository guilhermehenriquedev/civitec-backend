from rest_framework import permissions


class IsMasterAdmin(permissions.BasePermission):
    """
    Permissão para usuários MASTER_ADMIN.
    Permite acesso total a todas as funcionalidades.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_master_admin
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_master_admin


class IsSectorAdmin(permissions.BasePermission):
    """
    Permissão para usuários SECTOR_ADMIN.
    Permite acesso total dentro do próprio setor.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN tem acesso ao próprio setor
        if request.user.is_sector_admin:
            # Verificar se a view tem um setor específico
            sector = getattr(view, 'sector', None)
            if sector:
                return request.user.sector == sector
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN tem acesso ao próprio setor
        if request.user.is_sector_admin:
            # Verificar se o objeto pertence ao setor do usuário
            if hasattr(obj, 'sector'):
                return request.user.sector == obj.sector
            if hasattr(obj, 'user') and hasattr(obj.user, 'sector'):
                return request.user.sector == obj.user.sector
            return True
        
        return False


class IsSectorOperator(permissions.BasePermission):
    """
    Permissão para usuários SECTOR_OPERATOR.
    Permite operações básicas dentro do próprio setor.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN tem acesso ao próprio setor
        if request.user.is_sector_admin:
            sector = getattr(view, 'sector', None)
            if sector:
                return request.user.sector == sector
            return True
        
        # SECTOR_OPERATOR tem acesso ao próprio setor
        if request.user.is_sector_operator:
            sector = getattr(view, 'sector', None)
            if sector:
                return request.user.sector == sector
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN tem acesso ao próprio setor
        if request.user.is_sector_admin:
            if hasattr(obj, 'sector'):
                return request.user.sector == obj.sector
            if hasattr(obj, 'user') and hasattr(obj.user, 'sector'):
                return request.user.sector == obj.user.sector
            return True
        
        # SECTOR_OPERATOR tem acesso ao próprio setor
        if request.user.is_sector_operator:
            if hasattr(obj, 'sector'):
                return request.user.sector == obj.sector
            if hasattr(obj, 'user') and hasattr(obj.user, 'sector'):
                return request.user.sector == obj.user.sector
            return True
        
        return False


class IsEmployeeSelf(permissions.BasePermission):
    """
    Permissão para usuários EMPLOYEE.
    Permite acesso apenas aos próprios dados.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN e SECTOR_OPERATOR têm acesso ao próprio setor
        if request.user.is_sector_admin or request.user.is_sector_operator:
            sector = getattr(view, 'sector', None)
            if sector:
                return request.user.sector == sector
            return True
        
        # EMPLOYEE tem acesso limitado
        if request.user.is_employee:
            # Permitir apenas operações de leitura e criação
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method == 'POST':
                return True
            return False
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # MASTER_ADMIN tem acesso a tudo
        if request.user.is_master_admin:
            return True
        
        # SECTOR_ADMIN e SECTOR_OPERATOR têm acesso ao próprio setor
        if request.user.is_sector_admin or request.user.is_sector_operator:
            if hasattr(obj, 'sector'):
                return request.user.sector == obj.sector
            if hasattr(obj, 'user') and hasattr(obj.user, 'sector'):
                return request.user.sector == obj.user.sector
            return True
        
        # EMPLOYEE tem acesso apenas aos próprios dados
        if request.user.is_employee:
            if hasattr(obj, 'user'):
                return obj.user == request.user
            if hasattr(obj, 'employee') and hasattr(obj.employee, 'user'):
                return obj.employee.user == request.user
            return False
        
        return False


class IsSectorAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão que permite leitura para todos, mas escrita apenas para SECTOR_ADMIN.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsSectorAdmin().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsSectorAdmin().has_object_permission(request, view, obj)
