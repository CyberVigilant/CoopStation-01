from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login

from .forms import SignupForm, LoginForm
from .models import Student

def hello(request):
    return render(request, 'pages/homepage.html')

def register_view(request):
    signup_form = SignupForm()
    login_form = LoginForm()
    active_tab = "signup"

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "signup":
            active_tab = "signup"
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Ensure the Student profile exists (so we can show name/major in the navbar)
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "full_name": getattr(user, "username", ""),
                        "major": "",
                    },
                )
                auth_login(request, user)
                return redirect("opportunities")  # change to your page name
            else:
                messages.error(request, "Please fix the signup errors.")

        elif form_type == "login":
            active_tab = "login"
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = login_form.cleaned_data["user"]
                auth_login(request, user)
                return redirect("opportunities")
            else:
                messages.error(request, "Please fix the login errors.")

    return render(
        request,
        "pages/register.html",
        {
            "signup_form": signup_form,
            "login_form": login_form,
            "active_tab": active_tab,
        },
    )


def about_us(request):
    return render(request, 'pages/about-us.html')
def contact_us(request):
    return render(request, "pages/contact-us.html")

def terms_of_service(request):
    return render(request, "pages/terms-of-service.html")

def leaderboard(request):
    return render(request, "pages/leaderboard.html")
def privacy_policy(request):
    return render(request, "pages/privacy-policy.html")

from django.contrib.auth.decorators import login_required

@login_required
def opportunities(request):
    student_profile = Student.objects.filter(user=request.user).first()
    return render(
        request,
        "pages/opportunities.html",
        {"student_profile": student_profile},
    )
