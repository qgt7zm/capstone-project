"""
Views for myapp application.
"""
import json

from django.contrib import messages
from django.core import serializers
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
            if any_filter:
                filtered_results = (
                        filtered_results.filter(name__icontains=any_filter) |
                        filtered_results.filter(description__icontains=any_filter) |
                        filter_by_outcome_name(filtered_results, any_filter) |
                        filter_by_resource_citation(filtered_results, any_filter, "outcomes")
                )

            name_filter = request.POST.get("name", None)
            if name_filter:
                filtered_results = filtered_results.filter(name__icontains=name_filter)

            description_filter = request.POST.get("description", None)
            if description_filter:
                filtered_results = filtered_results.filter(description__icontains=description_filter)

            outcome_filter = request.POST.get("outcome", None)
            if outcome_filter:
                filtered_results = filter_by_outcome_name(filtered_results, outcome_filter)

            resource_filter = request.POST.get("resource", None)
            print("resource = " + resource_filter)
            if resource_filter:
                filtered_results = filter_by_resource_citation(filtered_results, resource_filter, "outcomes")

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
            if any_filter:
                filtered_results = (
                        filtered_results.filter(name__icontains=any_filter) |
                        filtered_results.filter(description__icontains=any_filter) |
                        filter_by_element_name(filtered_results, any_filter) |
                        filter_by_resource_citation(filtered_results, any_filter, "outcomes")
                )

            name_filter = request.POST.get("name", None)
            if name_filter:
                filtered_results = filtered_results.filter(name__icontains=name_filter)

            description_filter = request.POST.get("description", None)
            if description_filter:
                filtered_results = filtered_results.filter(description__icontains=description_filter)

            element_filter = request.POST.get("element", None)
            if element_filter:
                filtered_results = filter_by_element_name(filtered_results, element_filter)

            resource_filter = request.POST.get("resource", None)
            if resource_filter:
                filtered_results = filter_by_resource_citation(filtered_results, resource_filter, "outcomes")

    context = {
        "outcomes": filtered_results,
    }
    return render(
        request,
        "myapp/outcomes.html",
        context
    )


def resources(request) -> HttpResponse:
    filtered_results = order_by_citation(Resource.objects.all())

    # Filter results using form
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "search":
            any_filter = request.POST.get("any", None)
            if any_filter:
                filtered_results = (
                        filtered_results.filter(title__icontains=any_filter) |
                        filter_by_author_name(filtered_results, any_filter) |
                        filter_by_year_str(filtered_results, any_filter) |
                        filtered_results.filter(summary__icontains=any_filter)
                ).distinct()

            summary_filter = request.POST.get("summary", None)
            if summary_filter:
                filtered_results = filtered_results.filter(summary__icontains=summary_filter)

            name_filter = request.POST.get("name", None)
            if name_filter:
                filtered_results = filter_by_author_name(filtered_results, any_filter)

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
            # Add resource
            title = request.POST.get("title")
            year = request.POST.get("year")
            existing_resource = Resource.objects.filter(title=title, year=year)
            if existing_resource.exists():
                # Resource already exists
                messages.error(request, "A resource with that title and year already exists.")
                return redirect("myapp:resources")

            location = request.POST.get("location", "")
            url = request.POST.get("url", "")
            summary = request.POST.get("summary", "")
            resource = Resource.objects.create(
                title=title, year=year, publisher=location, url=url, summary=summary
            )

            # Add authors
            num_authors = int(request.POST.get("num_authors"))
            authors = []
            for i in range(1, num_authors + 1):
                first_name = request.POST.get(f"author{i}_first_name")
                last_name = request.POST.get(f"author{i}_last_name")
                existing_author = Author.objects.filter(first_name=first_name, last_name=last_name)
                if existing_author.exists():
                    # Author already exists
                    continue
                author = Author.objects.create(first_name=first_name, last_name=last_name)
                authors.append(author)

            # Link authors to resources
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
            # Add result
            resource = get_object_or_404(Resource, pk=resource_pk)

            rating_label = request.POST.get("rating")
            rating = get_choice_from_label(Result.ResultRatings, rating_label)

            subject_label = request.POST.get("subject")
            subject = get_choice_from_label(Result.Subjects, subject_label)

            age_group_label = request.POST.get("age_group")
            age_group = get_choice_from_label(Result.AgeGroups, age_group_label)

            sample_size = request.POST.get("sample_size")

            result = Result.objects.create(
                resource=resource,
                rating=rating, subject=subject, age_group=age_group,
                sample_size=sample_size
            )

            # Set elements and outcomes
            element_names = request.POST.getlist("elements")
            result_elements = Element.objects.filter(name__in=element_names)
            outcome_names = request.POST.getlist("outcomes")
            result_outcomes = Outcome.objects.filter(name__in=outcome_names)
            result.elements.set(result_elements)
            result.outcomes.set(result_outcomes)

            messages.success(request, "Result created successfully.")

    kwargs = {
        "resource_pk": resource_pk,
    }
    return redirect(reverse("myapp:resource_view", kwargs=kwargs))


def scenarios(request) -> HttpResponse:
    return render(
        request,
        "myapp/scenarios.html"
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
