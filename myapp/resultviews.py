"""
Result views for myapp application.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from myapp.models import Resource, Element, Outcome, ResultRatings, Subjects, AgeGroups, Result
from myapp.modelutils import get_choice_from_label


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
