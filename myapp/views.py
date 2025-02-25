"""
Views for myapp application.
"""
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import json

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


def data(request) -> HttpResponse:
    return render(
        request,
        "myapp/data.html"
    )


def data_export(request) -> HttpResponse:
    # Export data to json
    # Source: https://docs.djangoproject.com/en/5.1/topics/serialization/
    model_classes = [
        Author,
        Resource,
        ResourceAuthor,
    ]

    # Combine json arrays
    all_data = []
    for model_class in model_classes:
        model_data = model_class.objects.all().order_by("pk")
        json_str = serializers.serialize("json", model_data)
        all_data += json.loads(json_str)
    return JsonResponse(all_data, safe=False)  # Need to export array


def about(request) -> HttpResponse:
    return render(
        request,
        "myapp/about.html"
    )
