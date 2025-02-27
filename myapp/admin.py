"""Admin models for myapp application."""
from django.contrib import admin

from .models import model_classes

for model_class in model_classes:
    admin.site.register(model_class)
