#!/usr/bin/env python
"""
Test script to verify chat functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fooddelivery.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Booking, ChatMessage

def setup_test_scenario():
    """Create test scenario for chat"""
    print("Setting up test scenario...")
    
    # Get or create customer
    try:
        customer = User.objects.get(username='test_customer')
    except User.DoesNotExist:
        customer = User.objects.create_user(username='test_customer', password='test123')
        UserProfile.objects.create(user=customer, mobile='1234567890', role='customer')
    
    # Get delivery partner
    delivery_partner = User.objects.filter(userprofile__role='delivery_partner').first()
    
    # Create or get test booking
    booking, created = Booking.objects.get_or_create(
        customer=customer,
        defaults={
            'pickup_address': "Test Pickup Address",
            'delivery_address': "Test Delivery Address",
            'delivery_partner': delivery_partner,
            'status': 'assigned'
        }
    )
    
    if not created:
        booking.delivery_partner = delivery_partner
        booking.status = 'assigned'
        booking.save()
    
    print(f"✓ Test booking created: #{booking.id}")
    print(f"✓ Customer: {customer.username} (Mobile: {customer.userprofile.mobile})")
    print(f"✓ Delivery Partner: {delivery_partner.username} (Mobile: {delivery_partner.userprofile.mobile})")
    print(f"✓ Booking Status: {booking.status}")
    print(f"✓ Chat URL: http://127.0.0.1:8000/chat/{booking.id}/")
    
    return booking, customer, delivery_partner

if __name__ == '__main__':
    setup_test_scenario()
    print("\n🎯 Test scenario ready!")
    print("1. Start the server: python manage.py runserver")
    print("2. Login as customer (mobile: 1234567890, OTP: 1234)")
    print("3. Login as delivery partner (mobile: 9876543211, OTP: 1234)")
    print("4. Test chat functionality")