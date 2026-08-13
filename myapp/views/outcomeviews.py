"""
Outcome views for myapp application.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from myapp.models import Outcome
from .viewutils import filter_outcomes


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


def outcome_view(request, outcome_pk: int) -> HttpResponse:
    outcome = get_object_or_404(Outcome, pk=outcome_pk)

    context = {
        "outcome": outcome
    }
    return render(
        request,
        "myapp/outcome_view.html",
        context
    )


def add_outcome(request) -> HttpResponse:
    return render(
        request,
        "myapp/add_outcome.html"
    )


def add_outcome_form(request) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "add_outcome":
            # Add outcome
            name = request.POST.get("name")
            description = request.POST.get("description")
            existing_outcome = Outcome.objects.filter(name=name)
            if existing_outcome.exists():
                # Outcome already exists
                messages.error(request, "An outcome with that name already exists.")
                return redirect("myapp:outcomes")

            outcome = Outcome.objects.create(
                name=name, description=description
            )

            messages.success(request, f'Outcome {outcome} created successfully.')

    return redirect("myapp:outcomes")


def edit_outcome(request, outcome_pk: int) -> HttpResponse:
    outcome = get_object_or_404(Outcome, pk=outcome_pk)

    context = {
        "outcome": outcome,
    }
    return render(
        request,
        "myapp/edit_outcome.html",
        context
    )


def edit_outcome_form(request, outcome_pk: int) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "edit_outcome":
            outcome = get_object_or_404(Outcome, pk=outcome_pk)
            name = request.POST.get("name")
            description = request.POST.get("description")

            # Update outcome
            outcome.name = name;
            outcome.description = description
            outcome.save()

            messages.success(request, f'Outcome {outcome} modified successfully.')

    return redirect("myapp:outcome_view", outcome_pk=outcome_pk)
