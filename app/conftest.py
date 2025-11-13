"""
Pytest configuration for Django tests
"""
import os
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure(config):
    """Configure Django settings for pytest"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
    django.setup()