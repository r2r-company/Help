from django.urls import path
from . import views
from .views import PaymentServiceDeleteView, delete_payment

urlpatterns = [
    path('services/', views.payment_service_list, name='payment_service_list'),
    path('services/<int:pk>/', views.payment_service_detail, name='payment_service_detail'),
    path('services/create/', views.create_payment_service, name='create_payment_service'),
    path('services/<int:service_id>/add-payment/', views.create_payment, name='create_payment'),
    path('services/<int:pk>/payments/', views.payment_service_detail, name='payment_service_detail'),
    path('service/<int:pk>/delete/', PaymentServiceDeleteView.as_view(), name='payment_service_delete'),
    path('payment/delete/<int:pk>/', delete_payment, name='delete_payment'),

]
