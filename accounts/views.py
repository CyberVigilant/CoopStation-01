from django.shortcuts import render

# Create your views here.

def hello(request):
    return render(request, 'pages/homepage.html')

def register(request):
    return render(request, 'register.html')

def about_us(request):
    return render(request, 'pages/about-us.html')
def contact_us(request):
    return render(request, "contact-us.html")

def login_view(request):
    return render(request, "pages/login.html")

def signup(request):
    return render(request, "signup.html")

def terms_of_service(request):
    return render(request, "terms-of-service.html")

def privacy_policy(request):
    return render(request, "privacy-policy.html")