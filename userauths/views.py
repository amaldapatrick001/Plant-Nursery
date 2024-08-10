from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

def sign_up(request):
    if request.method == "POST":  
        form = UserRegisterForm(request.POST)
        if form.is_valid(): 
            new_user = form.save()  
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created successfully.")
            new_user = authenticate(username=form.cleaned_data.get("email"), password=form.cleaned_data['password1'])
            login(request, new_user)
            #return redirect('core:index.html') 
        else:
            messages.error(request, "User cannot be registered. Please correct the errors.")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)
