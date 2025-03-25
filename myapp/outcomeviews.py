"""
Outcome views for myapp application.
"""
from django.http import HttpResponse
from django.shortcuts import render

from myapp.models import Outcome
from myapp.viewutils import filter_outcomes


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
