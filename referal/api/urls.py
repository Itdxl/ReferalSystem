from django.urls import path
from . import views

urlpatterns = [
    path('send-code/', views.send_code, name='send_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('profile/', views.profile, name='profile'),
    path('invites-counter/', views.invites_counter, name='invites_counter'),
]
