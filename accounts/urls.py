from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.hello, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("register/", views.register_view, name="register"),
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("opportunities/", views.opportunities, name="opportunities"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]