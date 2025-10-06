from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from .models import *

from .forms import *
from django.shortcuts import render
from django.utils.timezone import now
from .models import Income, Expense
from itertools import chain
from operator import attrgetter
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required 


@login_required(login_url="SignIn")
def income(request):
    income = Income.objects.all().order_by("-id")

    context = {
        "income":income
    }
    return render(request,"finance/income.html",context)


@login_required(login_url="SignIn")
def add_income(request):
    form = IncomeForm()

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Income record added successfully.")
            return redirect('income')  # Redirect to the same page or another view
 
    return render(request, 'finance/add-income.html', {'form': form})

@login_required(login_url="SignIn")
def update_income(request,pk):
    income  = get_object_or_404(Income,id = pk)
    form = IncomeForm(instance=income)

    if request.method == 'POST':
        form = IncomeForm(request.POST,instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Income Update successfully.")
            return redirect('income')  # Redirect to the same page or another view
 
    return render(request, 'finance/update-income.html', {'form': form})


@login_required(login_url="SignIn")
def delete_income(request,pk):
    income = get_object_or_404(Income,id = pk)
    income.delete()
    messages.success(request,"Income deleted success.....")
    return redirect("income")



@login_required(login_url="SignIn")
def expense(request):
    ex = Expense.objects.all().order_by("-id")
    context = {
        "expense":ex
    }
    return render(request,"finance/Expense.html",context)


@login_required(login_url="SignIn")
def delete_expense(request,pk):
    expense = get_object_or_404(Expense,id = pk)
    expense.delete()
    messages.success(request,"Expense deleted success.....")
    return redirect("expense")


# View for adding expense
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense record added successfully.")
            return redirect('Expense')  # Redirect to the same page or another view
    else:
        form = ExpenseForm()
    return render(request, 'finance/add-expense.html', {'form': form})

def update_expense(request,pk):
    expense = get_object_or_404(Expense, id = pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST,instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense record added successfully.")
            return redirect('Expense')  # Redirect to the same page or another view
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'finance/update-expense.html', {'form': form})




def balance_sheet(request):
    # Get the current date
    current_date = now()
    month = current_date.strftime("%B")

    # Filter income and expenses for the current month
    income_list = Income.objects.filter(date__year=current_date.year, date__month=current_date.month)
    expense_list = Expense.objects.filter(date__year=current_date.year, date__month=current_date.month)

    # Convert to lists with 'type' field indicating credit (income) or debit (expense)
    income_data = [{'type': 'credit', 'date': income.date, 'perticulers': income.perticulers, 'amount': income.amount} for income in income_list]
    expense_data = [{'type': 'debit', 'date': expense.date, 'perticulers': expense.perticulers, 'amount': expense.amount} for expense in expense_list]

    # Combine both lists and order by date
    combined_list = sorted(
        chain(income_data, expense_data),
        key=lambda x: x['date']
    )

    # Calculate totals
    total_income = sum(income['amount'] for income in income_data)
    total_expense = sum(expense['amount'] for expense in expense_data)

    # Pass data to the template
    return render(request, "finance/balancesheet.html", {
        'combined_list': combined_list,
        'total_income': total_income,
        'total_expense': total_expense,
        "month":month
    })


from django.shortcuts import render
from django.utils.timezone import now
from .models import Income, Expense
from itertools import chain
from operator import attrgetter

def balance_sheet_selected(request):
    if request.method == "POST":
    # Get start and end dates from form submission (default to current month if not provided)
        start_date = request.POST.get('sdate')
        end_date = request.POST.get('edate')

    if start_date and end_date:
        # Filter by selected date range
        income_list = Income.objects.filter(date__range=[start_date, end_date])
        expense_list = Expense.objects.filter(date__range=[start_date, end_date])
    else:
        # Default to current month if no dates are provided
        current_date = now()
        income_list = Income.objects.filter(date__year=current_date.year, date__month=current_date.month)
        expense_list = Expense.objects.filter(date__year=current_date.year, date__month=current_date.month)

    # Convert to lists with 'type' field indicating credit (income) or debit (expense)
    income_data = [{'type': 'credit', 'date': income.date, 'perticulers': income.perticulers, 'amount': income.amount} for income in income_list]
    expense_data = [{'type': 'debit', 'date': expense.date, 'perticulers': expense.perticulers, 'amount': expense.amount} for expense in expense_list]

    # Combine both lists and order by date
    combined_list = sorted(
        chain(income_data, expense_data),
        key=lambda x: x['date']
    )

    # Calculate totals
    total_income = sum(income['amount'] for income in income_data)
    total_expense = sum(expense['amount'] for expense in expense_data)

    # Pass data to the template
    return render(request, "finance/balancesheet.html", {
        'combined_list': combined_list,
        'total_income': total_income,
        'total_expense': total_expense,
        'start_date': start_date,
        'end_date': end_date,
        "month": f"{start_date} to {end_date}"
    })



# in finance i am desided to add report generation through this application 
# below methods are the report generation 


def delete_bulk_income(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('contact_id[]')  # Get the selected IDs from the form
        print(selected_ids,"----------------------------------")
        if selected_ids:
            Income.objects.filter(id__in=selected_ids).delete()
            messages.success(request, 'Selected items have been deleted.')
        else:
            messages.warning(request, 'No items were selected for deletion.')
    return redirect("income")

def delete_bulk_expense(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('contact_id[]')  # Get the selected IDs from the form
        print(selected_ids,"----------------------------------")
        if selected_ids:
            Expense.objects.filter(id__in=selected_ids).delete()
            messages.success(request, 'Selected items have been deleted.')
        else:
            messages.warning(request, 'No items were selected for deletion.')
    return redirect("expense")