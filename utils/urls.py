from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    path('teachers/<int:pk>/disable/', views.disable_teacher, name='disable_teacher'),
    path('teachers/<int:pk>/enable/', views.enable_teacher, name='enable_teacher'),
    path('teachers/bulk-action/', views.bulk_action_teachers, name='bulk_action_teachers'),

# Attendance URLs
    path('attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/mark/<int:teacher_id>/', views.mark_attendance, name='mark_attendance_single'),
    path('attendance/bulk/', views.bulk_mark_attendance, name='bulk_mark_attendance'),
    path('attendance/list/', views.attendance_list, name='attendance_list'),
    path('attendance/teacher/<int:teacher_id>/', views.teacher_attendance_detail, name='teacher_attendance_detail'),
    
    # Salary URLs
    path('salary/', views.salary_dashboard, name='salary_dashboard'),
    path('salary/calculate/', views.calculate_monthly_salary, name='calculate_monthly_salary'),
    path('salary/list/', views.salary_list, name='salary_list'),
    path('salary/detail/<int:salary_id>/', views.salary_detail, name='salary_detail'),
    path('salary/payment/<int:salary_id>/', views.update_salary_payment, name='update_salary_payment'),
    path('salary/deductions/<int:salary_id>/', views.make_deductions, name='make_deductions'),
    path('salary/extra/<int:salary_id>/', views.make_extra_payment, name='make_extra_payment'),
]