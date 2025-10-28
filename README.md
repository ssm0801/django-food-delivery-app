# Food Delivery Web App (Lite Version)

A Django-based food delivery application with real-time chat functionality between customers and delivery partners.

## Features

- **Customer Features:**
  - Login via mobile number & OTP (static OTP: 1234)
  - Create, view, and cancel bookings
  - **Real-time WebSocket chat** with assigned delivery partner

- **Delivery Partner Features:**
  - View assigned bookings
  - Update booking status (Start → Reached → Collected → Delivered)
  - **Real-time WebSocket chat** with customers

- **Admin Features:**
  - View all bookings
  - Assign bookings to delivery partners
  - Manage users and system

## Tech Stack

- Django 4.2.7
- **Django Channels 4.0.0** (Real-time WebSocket support)
- **Redis 5.0.1** (Channel layers for WebSocket scaling)
- Bootstrap 5 (Frontend styling)
- Vanilla JavaScript (Real-time chat UI)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis server

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd django
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Setup initial data:**
   ```bash
   python manage.py setup_data
   ```

6. **Start Redis server:**
   ```bash
   redis-server
   ```

7. **Run the development server:**
   ```bash
   # Use the start script (recommended)
   ./start_dev.sh
   
   # Or manually start ASGI server for WebSocket support
   daphne -b 127.0.0.1 -p 8000 fooddelivery.asgi:application
   ```

## Default Users

After running `setup_data` command:

### Admin
- Username: `admin`
- Password: `admin123`
- Access: `/admin/` or login with mobile `9999999999`

### Delivery Partners
- Usernames: `delivery_1`, `delivery_2`, `delivery_3`
- Mobile: `9876543211`, `9876543212`, `9876543213`
- OTP: `1234`

### Customers
- Any mobile number with OTP `1234` creates a new customer account

## Usage Flow

1. **Customer Journey:**
   - Login with any mobile number + OTP (1234)
   - Create a new booking with pickup and delivery addresses
   - Wait for admin to assign a delivery partner
   - **Real-time WebSocket chat** with delivery partner once assigned
   - Track booking status updates in real-time

2. **Admin Journey:**
   - Login with admin credentials
   - View all pending bookings
   - Assign delivery partners to bookings
   - Monitor system activity

3. **Delivery Partner Journey:**
   - Login with delivery partner credentials
   - View assigned bookings
   - Update booking status through the workflow
   - **Real-time WebSocket chat** with customers

## API Endpoints

- `/` - Home page
- `/login/` - Login page
- `/customer/` - Customer dashboard
- `/delivery/` - Delivery partner dashboard
- `/admin/` - Admin dashboard
- `/simple-chat/<booking_id>/` - Real-time chat interface
