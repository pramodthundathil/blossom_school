from django.shortcuts import render, redirect, get_object_or_404 
"""
This module contains view functions for the home application of the Blossom School project.
Functions:
    - index(request): Renders the index (home) page of the application.
    - login(request): Handles user authentication and logs the user in.
    - logout(request): Logs the user out and redirects to the appropriate page.
    - authenticate(request): Authenticates user credentials for login.
Imports:
    - Django shortcuts for rendering templates, redirecting, and retrieving objects.
    - Django messages framework for displaying notifications.
    - Django authentication decorators and functions for managing user sessions.
    - Local models and forms for handling application-specific data and user input.
"""
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from .models import *
from .forms import *
from .decorators import unauthenticated_user

# authentications and dashboards 

@unauthenticated_user
def index(request):
    return render(request,"auth_templates/index.html")


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect("index")
        else:
            messages.error(request, "username or password incorrect")
            return redirect('signin')
    return render(request,"auth_templates/login.html")

def signout(request):
    logout(request)
    return redirect("signin")