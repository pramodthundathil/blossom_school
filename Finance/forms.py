from django import forms
from .models import Income, Expense

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['perticulers', 'amount', "bill_number", 'other']
        labels = {
            'perticulers': 'Particulars',
            'amount': 'Amount',
            'other': 'Partner Details',
        }
        widgets = {
            'perticulers': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'income-perticulers',
                'placeholder': 'Enter particulars'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-input',
                'id': 'income-amount',
                'placeholder': 'Enter amount',
                "min":0
            }),
            'other': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'income-other',
                'placeholder': 'Other details'
            }),
            'bill_number': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'billno',
                'placeholder': 'Bill Number (Optional)'
            }),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['perticulers',"bill_number", 'amount', 'other']
        labels = {
            'perticulers': 'Particulars',
            'amount': 'Amount',
            'other': 'Partner Details',
        }
        widgets = {
            'perticulers': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'Expense-perticulers',
                'placeholder': 'Enter particulars'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-input',
                'id': 'Expense-amount',
                'placeholder': 'Enter amount',
                "min":0
            }),
            'other': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'Expense-other',
                'placeholder': 'Other details',
               
            }),
            'bill_number': forms.TextInput(attrs={
                'class': 'form-control form-input',
                'id': 'billno',
                'placeholder': 'Bill Number (Optional)'
            }),
        }
