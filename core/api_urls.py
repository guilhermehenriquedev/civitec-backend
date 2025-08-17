"""
URLs da API do CiviTec
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, InviteViewSet, PublicInviteViewSet
from rh.views import EmployeeViewSet, VacationRequestViewSet, PayslipViewSet
from tributos.views import TaxpayerViewSet, InvoiceViewSet, AssessmentViewSet, BillingViewSet
from licitacao.views import ProcurementViewSet, ProcPhaseViewSet, ProposalViewSet, AwardViewSet, ContractViewSet, ContractMilestoneViewSet
from obras.views import WorkProjectViewSet, WorkProgressViewSet, WorkPhotoViewSet
from reporting.views import DashboardViewSet
from audit.views import AuditLogViewSet

# Configurar roteador da API
router = DefaultRouter()

# Usuários - IMPORTANTE: users deve vir antes de users/invites
router.register(r'users', UserViewSet)
router.register(r'invites', InviteViewSet, basename='invites')

# RH
router.register(r'rh/employees', EmployeeViewSet)
router.register(r'rh/vacations', VacationRequestViewSet)
router.register(r'rh/payslips', PayslipViewSet)

# Tributos
router.register(r'tributos/taxpayers', TaxpayerViewSet)
router.register(r'tributos/invoices', InvoiceViewSet)
router.register(r'tributos/assessments', AssessmentViewSet)
router.register(r'tributos/billings', BillingViewSet)

# Licitação
router.register(r'licitacao/procurements', ProcurementViewSet)
router.register(r'licitacao/phases', ProcPhaseViewSet)
router.register(r'licitacao/proposals', ProposalViewSet)
router.register(r'licitacao/awards', AwardViewSet)
router.register(r'licitacao/contracts', ContractViewSet)
router.register(r'licitacao/milestones', ContractMilestoneViewSet)

# Obras
router.register(r'obras/projects', WorkProjectViewSet)
router.register(r'obras/progress', WorkProgressViewSet)
router.register(r'obras/photos', WorkPhotoViewSet)

# Relatórios
router.register(r'reporting/dashboard', DashboardViewSet, basename='dashboard')

# Auditoria
router.register(r'audit/logs', AuditLogViewSet)

urlpatterns = [
    # Incluir URLs do roteador
    path('', include(router.urls)),
    
    # URLs de autenticação
    path('auth/', include('users.auth_urls')),
    
    # URLs públicas para convites
    path('public/invites/', include([
        path('validate/', PublicInviteViewSet.as_view({'post': 'validate'}), name='public-invite-validate'),
        path('accept/', PublicInviteViewSet.as_view({'post': 'accept'}), name='public-invite-accept'),
    ])),
    
    # URLs de relatórios específicos
    path('reporting/dashboard-master/', DashboardViewSet.as_view({'get': 'master_dashboard'}), name='master-dashboard'),
    path('reporting/dashboard-sector/<str:sector>/', DashboardViewSet.as_view({'get': 'sector_dashboard'}), name='sector-dashboard'),
]
