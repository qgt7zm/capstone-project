"""
Scenario views for myapp application.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from myapp.models import Scenario, Subjects, AgeGroups, Outcome
from myapp.modelutils import get_choice_from_label
from myapp.recommender import get_recommendations_combined
from .viewutils import filter_scenarios


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
