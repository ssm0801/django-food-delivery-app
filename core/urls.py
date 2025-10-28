from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('update-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('assign-booking/<int:booking_id>/', views.assign_booking, name='assign_booking'),
    path('chat/<int:booking_id>/', views.chat_view, name='chat'),

    path('simple-chat/<int:booking_id>/', views.simple_chat_view, name='simple_chat'),
]