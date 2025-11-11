from django.urls import path 
from . import views 


urlpatterns = [
    #auth and index functions profile handling and password settings 
    path("index/",views.index,name="index"),
    path("index_employee/",views.index_employee,name="index_employee"),
    
    path("", views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
    path('profile/',views.profile,name="profile"),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('profile/activity/', views.get_user_activity, name='user_activity'),

    
    #Settings of site including 

    path("settings",views.site_setting,name="site_setting"),
    path("update_class/<int:pk>",views.update_class,name="update_class"),
    path("delete_class/<int:pk>",views.delete_class,name="delete_class"),
    #fee Caategory
    path("fee_category/", views.fee_category, name="fee_category"),
    path("update_fee_category/<int:pk>/", views.update_fee_category, name="update_fee_category"),
    path("delete_fee_category/<int:pk>/", views.delete_fee_category, name="delete_fee_category"),




    #analytics and dash boards 

    path('reports_dashboard/', views.reports_dashboard, name='reports_dashboard'),
    path('daily/', views.generate_daily_report, name='generate_daily_report'),
    path('date-range/', views.generate_date_range_report, name='generate_date_range_report'),
    path('fee-tracking/', views.generate_fee_tracking_report, name='generate_fee_tracking_report'),
    path('student-report/', views.generate_student_report, name='generate_student_report'),

# API endpoints for dashboard data
    path('api/dashboard-data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/class-distribution/', views.get_class_distribution, name='class_distribution'),
    path('api/payment-status/', views.get_payment_status_chart, name='payment_status_chart'),
]
