from django.shortcuts import redirect
from django.contrib import messages


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request,*args,**kwargs)
        else:
            messages.info(request,"You are not logged in please login to continue")
            return redirect("signin")
        
    return wrapper_func

def user_controls(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "admin":
                return view_func(request, *args, **kwargs)
            
            else:
                return redirect("index_employee")
        else:
            messages.info(request,"You are not logged in please login to continue")
            return redirect("signin")
    return wrapper_func

