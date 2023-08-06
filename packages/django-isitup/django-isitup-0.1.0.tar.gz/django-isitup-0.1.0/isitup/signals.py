# isitup/signals.py
from django.conf import settings
from django.dispatch import Signal

response_error_received = Signal(providing_args=["host", "response_code"])
response_error_resolved = Signal(providing_args=["host", "response_code"])

