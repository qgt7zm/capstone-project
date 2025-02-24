"""Admin models for myapp application."""
from django.contrib import admin
from . import models

admin.site.register(models.Author)
admin.site.register(models.Resource)
admin.site.register(models.ResourceAuthor)
