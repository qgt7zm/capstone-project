"""
Views for myapp application.
"""
import json

from django.contrib import messages
from django.core import serializers
from django.db.models.functions import Cast
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse

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

    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "search":
            # Filter results using form
            any_filter = request.POST.get("any", None)
            filtered_results = (
                    filtered_results.filter(name__icontains=any_filter) |
                    filtered_results.filter(description__icontains=any_filter)
            )

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

    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "search":
            # Filter results using form
            any_filter = request.POST.get("any", None)
            filtered_results = (
                    filtered_results.filter(name__icontains=any_filter) |
                    filtered_results.filter(description__icontains=any_filter)
            )

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
    filtered_results = order_by_citation(Resource.objects.all())

    # Filter results using form
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "search":
            any_filter = request.POST.get("any", None)
            if any_filter:
                filtered_results = filtered_results.annotate(
                    year_str=Cast("year", output_field=models.CharField(max_length=100))
                )
                filtered_results = (
                        filtered_results.filter(title__icontains=any_filter) |
                        filtered_results.filter(authors__first_name__icontains=any_filter) |
                        filtered_results.filter(authors__last_name__icontains=any_filter) |
                        filtered_results.filter(year_str=any_filter) |
                        filtered_results.filter(summary__icontains=any_filter)
                ).distinct()

            summary_filter = request.POST.get("title", None)
            if summary_filter:
                filtered_results = filtered_results.filter(title__icontains=summary_filter)

            author_filter = request.POST.get("author", None)
            if author_filter:
                filtered_results = (
                        filtered_results.filter(authors__first_name__icontains=author_filter) |
                        filtered_results.filter(authors__last_name__icontains=author_filter)
                ).distinct()

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
    resource = get_object_or_404(Resource, pk=resource_pk)
    results = Result.objects.filter(resource=resource)

    context = {
        "resource": resource,
        "results": results,
    }
    return render(
        request,
        "myapp/resource_view.html",
        context
    )


def add_resource(request) -> HttpResponse:
    return render(
        request,
        "myapp/add_resource.html"
    )


def add_resource_form(request) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "add_resource":
            # Add Resource
            title = request.POST.get("title")
            year = request.POST.get("year")
            # TODO prevent duplicate title + year
            location = request.POST.get("location", "")
            url = request.POST.get("url", "")
            summary = request.POST.get("summary", "")
            resource = Resource.objects.create(
                title=title, year=year, publisher=location, url=url, summary=summary
            )

            # Add Authors
            num_authors = int(request.POST.get("num_authors"))
            authors = []
            for i in range(1, num_authors + 1):
                first_name = request.POST.get(f"author{i}_first_name")
                last_name = request.POST.get(f"author{i}_last_name")
                existing = Author.objects.filter(first_name=first_name, last_name=last_name)
                if existing.exists():
                    continue
                author = Author.objects.create(first_name=first_name, last_name=last_name)
                authors.append(author)

            # Add ResourceAuthors
            for i, author in enumerate(authors):
                ResourceAuthor.objects.create(resource=resource, author=author, order=i)

            messages.success(request, "Resource created successfully.")

    return redirect("myapp:resources")


def add_result(request, resource_pk: int) -> HttpResponse:
    resource = get_object_or_404(Resource, pk=resource_pk)
    context = {
        "resource": resource,
        "element_choices": [element.name for element in Element.objects.all()],
        "outcome_choices": [outcome.name for outcome in Outcome.objects.all()],
        "rating_choices": Result.ResultRatings.labels,
        "subject_choices": Result.Subjects.labels,
        "age_group_choices": Result.AgeGroups.labels,
    }
    return render(
        request,
        "myapp/add_result.html",
        context
    )


def add_result_form(request, resource_pk: int) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "add_result":
            # Add Result
            resource = get_object_or_404(Resource, pk=resource_pk)

            element_names = request.POST.getlist("elements")
            elements = Element.objects.filter(name__in=element_names)
            outcome_names = request.POST.getlist("outcomes")
            outcomes = Outcome.objects.filter(name__in=outcome_names)

            rating_label = request.POST.get("rating")
            rating = None
            for val, label in Result.ResultRatings.choices:
                if rating_label == label:
                    rating = val

            subject_label = request.POST.get("subject")
            subject = None
            for val, label in Result.Subjects.choices:
                if subject_label == label:
                    subject = val

            age_group_label = request.POST.get("age_group")
            age_group = None
            for val, label in Result.AgeGroups.choices:
                if age_group_label == label:
                    age_group = val

            sample_size = request.POST.get("sample_size")

            result = Result.objects.create(
                resource=resource,
                rating=rating, subject=subject, age_group=age_group,
                sample_size=sample_size
            )
            result.elements.set(elements)
            result.outcomes.set(outcomes)

            messages.success(request, "Result created successfully.")

    kwargs = {
        "resource_pk": resource_pk,
    }
    return redirect(reverse("myapp:resource_view", kwargs=kwargs))


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
                file = form.cleaned_data.get("file")
                model_data = serializers.deserialize("json", file)
                for model_obj in model_data:
                    model_obj.object.save()
                messages.success(request, "Data uploaded successfully.")
            except serializers.base.DeserializationError:
                messages.error(request, "Please use the Django models .json format.")
        else:
            messages.error(request, "Please select a .json file.")

    return redirect("myapp:data")


def data_delete(request) -> HttpResponse:
    if request.method == "POST":
        form = DeleteDataForm(request.POST)
        if form.is_valid():
            # DANGER: Delete all data
            for model_class in model_classes:
                model_class.objects.all().delete()

            messages.success(request, "Data deleted successfully.")
        else:
            messages.error(request, "Please use the button to delete data.")

    return redirect("myapp:data")


def about(request) -> HttpResponse:
    return render(
        request,
        "myapp/about.html"
    )
