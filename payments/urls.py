from django.urls import path
from . import views



urlpatterns = [
    # Dashboard and main views
    path('payment_dashboard/', views.PaymentDashboardView.as_view(), name='payment_dashboard'),
    path('list/', views.PaymentListView.as_view(), name='payment_list'),
    
    # Payment CRUD operations
    path('create/', views.create_payment, name='create_payment'),
    # path('create/<uuid:student_id>', views.create_payment, name='create_payment'),
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Student payment management
    path('student/<uuid:student_id>/', views.student_payment_details, name='student_payment_details'),
    path('student/<uuid:student_id>/outstanding/', views.get_student_outstanding_fees, name='student_outstanding_fees'),
    
    # Payment plans
    path('plan/create/<uuid:student_id>/', views.create_payment_plan, name='create_payment_plan'),
    
    # Reports
    path('reports/overdue/', views.overdue_payments_report, name='overdue_report'),
    path('reports/summary/', views.payment_summary_report, name='payment_summary_report'),
    path('reports/defaulters/', views.defaulter_report, name='defaulter_report'),
    path('reports/export/', views.export_payment_data, name='export_payment_data'),
    
    # Bulk operations
    path('reminders/bulk/', views.bulk_payment_reminder, name='bulk_reminder'),
    
    # AJAX endpoints
    path('ajax/fee-structure/', views.get_fee_structure_amount, name='get_fee_structure_amount'),
    path('ajax/validate-amount/', views.validate_payment_amount, name='validate_payment_amount'),
]