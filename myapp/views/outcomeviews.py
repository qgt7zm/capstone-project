"""
Outcome views for myapp application.
"""
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

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
