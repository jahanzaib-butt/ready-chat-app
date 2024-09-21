from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page after registration
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {"form": form})

def login_view(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {"form": form})



from django.contrib.auth.decorators import login_required

@login_required
def some_view(request):
    # Your view logic here
    pass
