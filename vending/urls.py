from django.urls import path
from . import views

urlpatterns = [
    path('', views.vending_machine, name='vending_machine'),
    path('process_purchase/', views.process_purchase, name='process_purchase'),
    path('history/', views.transaction_history, name='transaction_history'),
]