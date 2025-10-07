# urls.py
from django.urls import path
from . import views



urlpatterns = [
    # Main student views
    path('students/', views.student_list, name='students'),

    path('create/', views.student_create, name='student_create'),
    path('student_detail/<uuid:pk>/', views.student_detail, name='student_detail'),
    path('student_update/<uuid:pk>/edit/', views.student_update, name='student_update'),
    path('student_update/<uuid:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Student status management
    path('<uuid:pk>/disable/', views.disable_student, name='disable_student'),
    path('<uuid:pk>/enable/', views.enable_student, name='enable_student'),
    
    # Document management
    path('<uuid:pk>/upload-document/', views.upload_document, name='upload_document'),
    path('document/delete/<uuid:pk>', views.delete_document, name='delete_document'),

    #add notes 
      
    path('<uuid:pk>/add/notes/', views.add_notes, name='add_notes'),
    path('notes/delete/<uuid:pk>', views.delete_notes, name='delete_note'),

    #add transportation
    path("transportation/add/<uuid:student_id>",views.add_transportation,name="add_transportation"),    
    # Bulk actions and exports
    path('bulk-action/', views.bulk_action, name='bulk_action'),
    path('export/', views.export_students, name='export_students'),
    
    # AJAX endpoints
    path('ajax/search/', views.search_students_ajax, name='search_students_ajax'),
    path('ajax/stats/', views.student_stats_ajax, name='student_stats_ajax'),

    # AJAX validation endpoint
    path('students/validate-field/', views.student_validate_field, name='student_validate_field'),
]