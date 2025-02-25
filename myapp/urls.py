"""
URL configuration for myapp application.
"""

from django.urls import path

from . import views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("elements", views.elements, name="elements"),
    path("scenarios", views.scenarios, name="scenarios"),
    path("resources", views.resources, name="resources"),
    path("data", views.data, name="data"),
    path("data/export", views.data_export, name="data_export"),
    path("data/upload", views.data_upload, name="data_upload"),
    path("data/delete", views.data_delete, name="data_delete"),
    path("about", views.about, name="about"),
]
