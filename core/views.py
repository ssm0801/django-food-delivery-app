from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from .models import UserProfile, Booking, ChatMessage

def home(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'customer':
                return redirect('customer_dashboard')
            elif profile.role == 'delivery_partner':
                return redirect('delivery_dashboard')
            elif profile.role == 'admin':
                return redirect('admin_dashboard')
        except UserProfile.DoesNotExist:
            pass
    return render(request, 'core/home.html')

def login_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        otp = request.POST.get('otp')
        
        if otp == '1234':  # Static OTP
            try:
                profile = UserProfile.objects.get(mobile=mobile)
                user = profile.user
                login(request, user)
                return redirect('home')
            except UserProfile.DoesNotExist:
                # Create new customer
                username = f"user_{mobile}"
                user = User.objects.create_user(username=username, password='temp123')
                UserProfile.objects.create(user=user, mobile=mobile, role='customer')
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def customer_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'customer':
            messages.error(request, 'Access denied. Customer access required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'core/customer_dashboard.html', {'bookings': bookings})

@login_required
def create_booking(request):
    if request.method == 'POST':
        pickup = request.POST.get('pickup_address')
        delivery = request.POST.get('delivery_address')
        
        Booking.objects.create(
            customer=request.user,
            pickup_address=pickup,
            delivery_address=delivery
        )
        messages.success(request, 'Booking created successfully!')
        return redirect('customer_dashboard')
    
    return render(request, 'core/create_booking.html')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status in ['pending', 'assigned']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
    return redirect('customer_dashboard')

@login_required
def delivery_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'delivery_partner':
            messages.error(request, 'Access denied. Delivery partner access required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    # Show all assigned bookings (not delivered or cancelled)
    bookings = Booking.objects.filter(
        delivery_partner=request.user
    ).exclude(
        status__in=['delivered', 'cancelled']
    ).order_by('-created_at')
    
    return render(request, 'core/delivery_dashboard.html', {'bookings': bookings})

@login_required
def update_booking_status(request, booking_id):
    # Check delivery partner access
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'delivery_partner':
            messages.error(request, 'Access denied. Delivery partner access required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id, delivery_partner=request.user)
    
    # Define the status flow: assigned → start → reached → collected → delivered
    status_flow = {
        'assigned': 'start',
        'start': 'reached', 
        'reached': 'collected',
        'collected': 'delivered'
    }
    
    if booking.status in status_flow:
        old_status = booking.get_status_display()
        booking.status = status_flow[booking.status]
        booking.save()
        new_status = booking.get_status_display()
        messages.success(request, f'Booking #{booking.id} status updated from {old_status} to {new_status}')
    else:
        messages.error(request, f'Cannot update status from {booking.get_status_display()}')
    
    return redirect('delivery_dashboard')

@login_required
def admin_dashboard(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin':
            messages.error(request, 'Access denied. Admin access required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    bookings = Booking.objects.all().order_by('-created_at')
    delivery_partners = User.objects.filter(userprofile__role='delivery_partner')
    return render(request, 'core/admin_dashboard.html', {
        'bookings': bookings,
        'delivery_partners': delivery_partners
    })

@login_required
def assign_booking(request, booking_id):
    # Check admin access
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin':
            messages.error(request, 'Access denied. Admin access required.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        partner_id = request.POST.get('delivery_partner')
        
        # Only assign if booking is pending
        if booking.status != 'pending':
            messages.error(request, 'Can only assign pending bookings.')
            return redirect('admin_dashboard')
        
        if partner_id:
            partner = get_object_or_404(User, id=partner_id)
            # Verify the partner is actually a delivery partner
            try:
                partner_profile = UserProfile.objects.get(user=partner)
                if partner_profile.role != 'delivery_partner':
                    messages.error(request, 'Selected user is not a delivery partner.')
                    return redirect('admin_dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Invalid delivery partner selected.')
                return redirect('admin_dashboard')
            
            booking.delivery_partner = partner
            booking.status = 'assigned'
            booking.save()
            messages.success(request, f'Booking #{booking.id} assigned to {partner_profile.mobile} successfully!')
        else:
            messages.error(request, 'Please select a delivery partner.')
    
    return redirect('admin_dashboard')

@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    profile = UserProfile.objects.get(user=request.user)
    
    # Check if user has access to this chat
    if not (booking.customer == request.user or booking.delivery_partner == request.user):
        messages.error(request, 'You do not have access to this chat')
        return redirect('home')
    
    # Only allow chat if booking is assigned (not pending or cancelled)
    if booking.status in ['pending', 'cancelled']:
        messages.error(request, 'Chat not available. Booking must be assigned to a delivery partner.')
        if profile.role == 'customer':
            return redirect('customer_dashboard')
        else:
            return redirect('delivery_dashboard')
    
    # Ensure booking has a delivery partner assigned
    if not booking.delivery_partner:
        messages.error(request, 'No delivery partner assigned to this booking yet.')
        return redirect('customer_dashboard' if profile.role == 'customer' else 'delivery_dashboard')
    
    chat_messages = ChatMessage.objects.filter(booking=booking)
    return render(request, 'core/chat.html', {
        'booking': booking,
        'messages': chat_messages
    })



@login_required
def simple_chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    profile = UserProfile.objects.get(user=request.user)
    
    # Check access
    if not (booking.customer == request.user or booking.delivery_partner == request.user):
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if booking.status in ['pending', 'cancelled'] or not booking.delivery_partner:
        messages.error(request, 'Chat not available')
        return redirect('customer_dashboard' if profile.role == 'customer' else 'delivery_dashboard')
    
    chat_messages = ChatMessage.objects.filter(booking=booking).order_by('timestamp')
    return render(request, 'core/chat_simple.html', {
        'booking': booking,
        'messages': chat_messages
    })