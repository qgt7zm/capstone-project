"""
Main views for myapp application.
"""
import json

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse

from .forms import *
from .models import *
from .recommender import get_recommendations_combined
from .viewutils import *


def index(request) -> HttpResponse:
    return redirect("myapp:home")


def home(request) -> HttpResponse:
    return render(
        request,
        "myapp/home.html"
    )


def elements(request) -> HttpResponse:
    filtered_elements = Element.objects.all()
    form_fields = {}

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            filtered_elements = filter_elements(
                request, filtered_elements, form_fields
            )

    context = {
        "elements": filtered_elements,
        "form_fields": form_fields,
    }
    return render(
        request,
        "myapp/elements.html",
        context
    )


def outcomes(request) -> HttpResponse:
    filtered_outcomes = Outcome.objects.all()
    form_fields = {}

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            filtered_outcomes = filter_outcomes(
                request, filtered_outcomes, form_fields
            )

    context = {
        "outcomes": filtered_outcomes,
        "form_fields": form_fields,
    }
    return render(
        request,
        "myapp/outcomes.html",
        context
    )


def add_result(request, resource_pk: int) -> HttpResponse:
    resource = get_object_or_404(Resource, pk=resource_pk)
    context = {
        "resource": resource,
        "element_choices": [element.name for element in Element.objects.all()],
        "outcome_choices": [outcome.name for outcome in Outcome.objects.all()],
        "rating_choices": ResultRatings.labels,
        "subject_choices": Subjects.labels,
        "age_group_choices": AgeGroups.labels,
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
            rating = get_choice_from_label(ResultRatings, rating_label)

            subject_label = request.POST.get("subject")
            subject = get_choice_from_label(Subjects, subject_label)

            age_group_label = request.POST.get("age_group")
            age_group = get_choice_from_label(AgeGroups, age_group_label)

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
    filtered_scenarios = Scenario.objects.all()
    form_fields = {}

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            filtered_scenarios = filter_scenarios(
                request, filtered_scenarios, form_fields
            )

    context = {
        "scenarios": filtered_scenarios,
        "form_fields": form_fields,
        "subject_choices": Subjects.labels,
        "age_group_choices": AgeGroups.labels,
    }
    return render(
        request,
        "myapp/scenarios.html",
        context
    )


def scenario_view(request, scenario_pk: int) -> HttpResponse:
    scenario = get_object_or_404(Scenario, pk=scenario_pk)
    recommendations = get_recommendations_combined(scenario)

    context = {
        "scenario": scenario,
        "recommendations": recommendations,
    }
    return render(
        request,
        "myapp/scenario_view.html",
        context
    )


def add_scenario(request) -> HttpResponse:
    context = {
        "outcome_choices": [outcome.name for outcome in Outcome.objects.all()],
        "subject_choices": Subjects.labels,
        "age_group_choices": AgeGroups.labels,
    }

    return render(
        request,
        "myapp/add_scenario.html",
        context
    )


def add_scenario_form(request) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "add_scenario":
            name = request.POST.get("name")
            existing_scenario = Scenario.objects.filter(name=name)

            new_name = name
            counter = 1
            while existing_scenario.exists():
                # Scenario already exists
                new_name = f"{name} ({counter})"
                existing_scenario = Scenario.objects.filter(name=new_name)
                counter += 1

            outcome_names = request.POST.getlist("outcomes")
            scenario_outcomes = Outcome.objects.filter(name__in=outcome_names)

            subject_label = request.POST.get("subject", None)
            subject = get_choice_from_label(Subjects, subject_label)
            age_group_label = request.POST.get("age_group", None)
            age_group = get_choice_from_label(AgeGroups, age_group_label)

            # Create Scenario
            scenario = Scenario.objects.create(
                name=new_name, subject=subject, age_group=age_group
            )
            scenario.outcomes.set(scenario_outcomes)

            messages.success(request, f'Scenario "{new_name}" created successfully.')

    return redirect("myapp:scenarios")


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
