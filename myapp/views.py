"""
Views for myapp application.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request) -> HttpResponse:
    return HttpResponseRedirect(reverse("myapp:home"))


def home(request) -> HttpResponse:
    return render(
        request,
        "myapp/home.html"
    )


def elements(request) -> HttpResponse:
    return render(
        request,
        "myapp/elements.html"
    )


def scenarios(request) -> HttpResponse:
    return render(
        request,
        "myapp/scenarios.html"
    )


def resources(request) -> HttpResponse:
    context = {
        "resources": Resource.objects.all(),
    }
    return render(
        request,
        "myapp/resources.html",
        context
    )


def about(request) -> HttpResponse:
    return render(
        request,
        "myapp/about.html"
    )
