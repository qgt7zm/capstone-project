"""
Main views for myapp application.
"""

from django.http import HttpResponse
from django.shortcuts import redirect, render


def index(request) -> HttpResponse:
    return redirect("myapp:home")


def home(request) -> HttpResponse:
    return render(
        request,
        "myapp/home.html"
    )


def data(request) -> HttpResponse:
    return render(
        request,
        "myapp/data.html"
    )


def about(request) -> HttpResponse:
    return render(
        request,
        "myapp/about.html"
    )
