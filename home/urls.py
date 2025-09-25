from django.urls import path 
from . import views 


urlpatterns = [
    #auth and index functions profile handling and password settings 
    path("index/",views.index,name="index"),
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

# ''' Need to be created'''

    #Finance management and fee collections 

# ''' Need to be created'''


    #staff management and salary calculations 

# ''' Need to be created'''


    #analytics and dash boards 


]
