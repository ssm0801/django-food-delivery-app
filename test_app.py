#!/usr/bin/env python
"""
Simple test script to verify the Food Delivery App functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fooddelivery.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Booking, ChatMessage

def test_user_creation():
    """Test user creation and roles"""
    print("Testing user creation and roles...")
    
    # Check admin user
    admin = User.objects.get(username='admin')
    admin_profile = UserProfile.objects.get(user=admin)
    assert admin_profile.role == 'admin'
    assert admin_profile.mobile == '9999999999'
    print("✓ Admin user created correctly")
    
    # Check delivery partners
    delivery_partners = User.objects.filter(userprofile__role='delivery_partner')
    assert delivery_partners.count() == 3
    print("✓ Delivery partners created correctly")
    
    # Create a test customer
    customer = User.objects.create_user(username='test_customer', password='test123')
    customer_profile = UserProfile.objects.create(
        user=customer,
        mobile='1234567890',
        role='customer'
    )
    print("✓ Test customer created")
    
    return customer, admin, delivery_partners.first()

def test_booking_flow(customer, admin, delivery_partner):
    """Test booking creation and assignment flow"""
    print("\nTesting booking flow...")
    
    # Create booking
    booking = Booking.objects.create(
        customer=customer,
        pickup_address="123 Main St, City A",
        delivery_address="456 Oak Ave, City B"
    )
    assert booking.status == 'pending'
    print("✓ Booking created with pending status")
    
    # Assign delivery partner (admin action)
    booking.delivery_partner = delivery_partner
    booking.status = 'assigned'
    booking.save()
    print("✓ Booking assigned to delivery partner")
    
    # Test status flow
    status_flow = ['assigned', 'start', 'reached', 'collected', 'delivered']
    for i, status in enumerate(status_flow[1:], 1):
        booking.status = status
        booking.save()
        print(f"✓ Status updated to: {status}")
    
    return booking

def test_chat_functionality(booking, customer, delivery_partner):
    """Test chat message creation"""
    print("\nTesting chat functionality...")
    
    # Reset booking to assigned status for chat testing
    booking.status = 'assigned'
    booking.save()
    
    # Create chat messages
    msg1 = ChatMessage.objects.create(
        booking=booking,
        sender=customer,
        message="Hello, when will you pick up my order?"
    )
    
    msg2 = ChatMessage.objects.create(
        booking=booking,
        sender=delivery_partner,
        message="I'll be there in 10 minutes!"
    )
    
    messages = ChatMessage.objects.filter(booking=booking)
    assert messages.count() == 2
    print("✓ Chat messages created successfully")
    
    return messages

def main():
    """Run all tests"""
    print("Starting Food Delivery App Tests...\n")
    
    try:
        # Test user creation
        customer, admin, delivery_partner = test_user_creation()
        
        # Test booking flow
        booking = test_booking_flow(customer, admin, delivery_partner)
        
        # Test chat functionality
        messages = test_chat_functionality(booking, customer, delivery_partner)
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✓")
        print("="*50)
        print("\nApp Summary:")
        print(f"- Total Users: {User.objects.count()}")
        print(f"- Total Bookings: {Booking.objects.count()}")
        print(f"- Total Chat Messages: {ChatMessage.objects.count()}")
        print(f"- Admin Users: {UserProfile.objects.filter(role='admin').count()}")
        print(f"- Delivery Partners: {UserProfile.objects.filter(role='delivery_partner').count()}")
        print(f"- Customers: {UserProfile.objects.filter(role='customer').count()}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()