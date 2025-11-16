"""
Pytest configuration for Django tests
"""
import os
import sys
from pathlib import Path
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure(config):
    """Configure Django settings for pytest"""
    app_dir = Path(__file__).resolve().parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.test_settings')
    django.setup()