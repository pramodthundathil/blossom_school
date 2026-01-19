from django.urls import path
from . import views



urlpatterns = [
    # Dashboard and main views
    path('payment_dashboard/', views.PaymentDashboardView.as_view(), name='payment_dashboard'),
    path('list/', views.PaymentListView.as_view(), name='payment_list'),
    path('pending/', views.PendingInstallmentListView.as_view(), name='pending_installments'),
    
    # Payment CRUD operations
    path('create/', views.create_payment, name='create_payment'),
    # path('create/<uuid:student_id>', views.create_payment, name='create_payment'),
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    
    # Student payment management
    path('student/<uuid:student_id>/', views.student_payment_details, name='student_payment_details'),
    path('student/<uuid:student_id>/outstanding/', views.get_student_outstanding_fees, name='student_outstanding_fees'),
    path('student/installment/marked/<int:pk>/',views.mark_as_paid,name="mark_as_paid"),
    # Payment plans
    path('plan/create/<uuid:student_id>/', views.create_payment_plan, name='create_payment_plan'),
    path('plan/edit/<int:pk>/', views.edit_payment_plan, name='edit_payment_plan'),
    path('plan/delete/<int:pk>/', views.delete_payment_plan, name='delete_payment_plan'),
    path('installment/edit/<int:pk>/', views.edit_payment_installment, name='edit_payment_installment'),
    path('plan/<int:plan_id>/add-installment/', views.add_payment_installment, name='add_payment_installment'),
    path('installment/delete/<int:pk>/', views.delete_payment_installment, name='delete_payment_installment'),
    path('installment/hold/<int:pk>/', views.hold_payment_installment, name='hold_payment_installment'),
    
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

    #invoice 
    path('invoice/<int:payment_id>/', views.generate_invoice, name='generate_invoice'),
    path('invoice/<int:payment_id>/pdf/', views.generate_invoice_quick, name='generate_invoice_pdf'),
]