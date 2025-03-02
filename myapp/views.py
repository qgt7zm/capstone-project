"""
Views for myapp application.
"""
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

import json

from .forms import *
from .models import *


def index(request) -> HttpResponse:
    return redirect("myapp:home")


def home(request) -> HttpResponse:
    return render(
        request,
        "myapp/home.html"
    )


def elements(request) -> HttpResponse:
    filtered_results = Element.objects.all()

    # Filter results using form
    if request.method == "POST":
        is_any = request.POST.get("is_any", None)
        if is_any == "1":
            any_filter = request.POST.get("any", None)
            filtered_results = (filtered_results.filter(name__icontains=any_filter) |
                                filtered_results.filter(description__icontains=any_filter))
        elif is_any == "0":
            name_filter = request.POST.get("name", None)
            if name_filter:
                filtered_results = filtered_results.filter(name__icontains=name_filter)

            description_filter = request.POST.get("description", None)
            if description_filter:
                filtered_results = filtered_results.filter(description__icontains=description_filter)

    context = {
        "elements": filtered_results,
    }
    return render(
        request,
        "myapp/elements.html",
        context
    )


def outcomes(request) -> HttpResponse:
    filtered_results = Outcome.objects.all()

    # Filter results using form
    if request.method == "POST":
        is_any = request.POST.get("is_any", None)
        if is_any == "1":
            any_filter = request.POST.get("any", None)
            filtered_results = (filtered_results.filter(name__icontains=any_filter) |
                                filtered_results.filter(description__icontains=any_filter))
        elif is_any == "0":
            name_filter = request.POST.get("name", None)
            if name_filter:
                filtered_results = filtered_results.filter(name__icontains=name_filter)

            description_filter = request.POST.get("description", None)
            if description_filter:
                filtered_results = filtered_results.filter(description__icontains=description_filter)

    context = {
        "outcomes": filtered_results,
    }
    return render(
        request,
        "myapp/outcomes.html",
        context
    )


def scenarios(request) -> HttpResponse:
    return render(
        request,
        "myapp/scenarios.html"
    )


def resources(request) -> HttpResponse:
    filtered_results = Resource.objects.all()

    # Filter results using form
    if request.method == "POST":
        is_any = request.POST.get("is_any", None)
        if is_any == "1":
            any_filter = request.POST.get("any", None)
            filtered_results = (filtered_results.filter(title__icontains=any_filter) |
                                filtered_results.filter(summary__icontains=any_filter))
        elif is_any == "0":
            summary_filter = request.POST.get("title", None)
            if summary_filter:
                filtered_results = filtered_results.filter(title__icontains=summary_filter)

            author_filter = request.POST.get("author", None)
            if author_filter:
                filtered_results = ((filtered_results.filter(authors__first_name__icontains=author_filter) |
                                    filtered_results.filter(authors__last_name__icontains=author_filter))
                                    .distinct())

            year = request.POST.get("year", None)
            if year:
                filtered_results = filtered_results.filter(year=year)

            summary_filter = request.POST.get("summary", None)
            if summary_filter:
                filtered_results = filtered_results.filter(summary__icontains=summary_filter)

    context = {
        "resources": filtered_results
    }
    return render(
        request,
        "myapp/resources.html",
        context
    )


def resource_view(request, resource_pk: int) -> HttpResponse:
    context = {
        "resource": get_object_or_404(Resource, pk=resource_pk)
    }
    return render(
        request,
        "myapp/resource_view.html",
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
