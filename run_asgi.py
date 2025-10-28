#!/usr/bin/env python3
"""
Simple ASGI server runner for development
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fooddelivery.settings')
    django.setup()
    
    # Use Django's runserver which supports ASGI when channels is installed
    execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])