from django.urls import path 
from .import views

urlpatterns = [
    path("income",views.income, name= "income"),
    path("expense",views.expense, name= "expense"),
    path("balance_sheet",views.balance_sheet, name= "balance_sheet"),
    path("balance_sheet_selected",views.balance_sheet_selected, name= "balance_sheet_selected"),
    path('add_income/', views.add_income, name='add_income'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('delete_income/<int:pk>', views.delete_income, name='delete_income'),
    path('delete_expense/<int:pk>', views.delete_expense, name='delete_expense'),
    path('update_income/<int:pk>', views.update_income, name='update_income'),
    path('update_expense/<int:pk>', views.update_expense, name='update_expense'),

    path("delete_bulk_income",views.delete_bulk_income,name="delete_bulk_income"),
    path("delete_bulk_expense",views.delete_bulk_expense,name="delete_bulk_expense"),


    
    
]