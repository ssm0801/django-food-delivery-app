from django.contrib import admin
from .models import UserProfile, Booking, ChatMessage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'role']
    list_filter = ['role']
    search_fields = ['mobile', 'user__username']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'delivery_partner', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'delivery_partner__username']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['booking', 'sender', 'message', 'timestamp']
    list_filter = ['timestamp']