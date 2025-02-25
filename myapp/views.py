"""
Views for myapp application.
"""
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

import json

from .forms import *
from .models import *

model_classes = [
    Author,
    Resource,
    ResourceAuthor,
]


def index(request) -> HttpResponse:
    return redirect("myapp:home")


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

    # Combine json arrays
    all_data = []
    for model_class in model_classes:
        model_data = model_class.objects.all().order_by("pk")
        # Exports to json array
        json_str = serializers.serialize("json", model_data)
        all_data += json.loads(json_str)
    return JsonResponse(all_data, safe=False)  # Need to export array


def data_upload(request) -> HttpResponse:
    if request.method == "POST":
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Import data from json
                # Must be a json array
                file = request.FILES["file"]
                model_data = serializers.deserialize("json", file)
                for model_obj in model_data:
                    model_obj.object.save()

                messages.success(request, "Data uploaded successfully.")
            except serializers.base.DeserializationError:
                messages.warning(request, "Please use the Django models .json format.")
        else:
            messages.warning(request, "Please select a .json file.")
        return redirect("myapp:data")

    return redirect("myapp:data")


def data_delete(request) -> HttpResponse:
    if request.method == "POST":
        print(request.POST)
        form = DeleteDataForm(request.POST)
        if form.is_valid():
            # DANGER: Delete all data
            for model_class in model_classes:
                model_class.objects.all().delete()

            messages.success(request, "Data deleted successfully.")
        else:
            messages.warning(request, "Please use the button to delete data.")
        return redirect("myapp:data")

    return redirect("myapp:data")


def about(request) -> HttpResponse:
    return render(
        request,
        "myapp/about.html"
    )
