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
from .modelutils import *
from .recommender import get_recommendations_combined


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
            # Filter results using form
            any_filter = request.GET.get("any", None)
            form_fields["any"] = any_filter
            if any_filter:
                filtered_elements = (
                        filtered_elements.filter(name__icontains=any_filter) |
                        filtered_elements.filter(description__icontains=any_filter) |
                        filter_by_outcome_name(filtered_elements, any_filter) |
                        filter_by_resource_citation(filtered_elements, any_filter, "outcomes")
                )

            name_filter = request.GET.get("name", None)
            form_fields["name"] = name_filter
            if name_filter:
                filtered_elements = filtered_elements.filter(name__icontains=name_filter)

            description_filter = request.GET.get("description", None)
            form_fields["description"] = description_filter
            if description_filter:
                filtered_elements = filtered_elements.filter(description__icontains=description_filter)

            outcome_filter = request.GET.get("outcome", None)
            form_fields["outcome"] = outcome_filter
            if outcome_filter:
                filtered_elements = filter_by_outcome_name(filtered_elements, outcome_filter)

            resource_filter = request.GET.get("resource", None)
            form_fields["resource"] = resource_filter
            if resource_filter:
                filtered_elements = filter_by_resource_citation(filtered_elements, resource_filter, "outcomes")

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
            # Filter results using form
            any_filter = request.GET.get("any", None)
            form_fields["any"] = any_filter
            if any_filter:
                filtered_outcomes = (
                        filtered_outcomes.filter(name__icontains=any_filter) |
                        filtered_outcomes.filter(description__icontains=any_filter) |
                        filter_by_element_name(filtered_outcomes, any_filter) |
                        filter_by_resource_citation(filtered_outcomes, any_filter, "outcomes")
                )

            name_filter = request.GET.get("name", None)
            form_fields["name"] = name_filter
            if name_filter:
                filtered_outcomes = filtered_outcomes.filter(name__icontains=name_filter)

            description_filter = request.GET.get("description", None)
            form_fields["description"] = description_filter
            if description_filter:
                filtered_outcomes = filtered_outcomes.filter(description__icontains=description_filter)

            element_filter = request.GET.get("element", None)
            form_fields["element"] = element_filter
            if element_filter:
                filtered_outcomes = filter_by_element_name(filtered_outcomes, element_filter)

            resource_filter = request.GET.get("resource", None)
            form_fields["resource"] = resource_filter
            if resource_filter:
                filtered_outcomes = filter_by_resource_citation(filtered_outcomes, resource_filter, "outcomes")

    context = {
        "outcomes": filtered_outcomes,
        "form_fields": form_fields,
    }
    return render(
        request,
        "myapp/outcomes.html",
        context
    )


def resources(request) -> HttpResponse:
    filtered_resources = order_by_citation(Resource.objects.all())
    form_fields = {}

    # Filter results using form
    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            any_filter = request.GET.get("any", None)
            form_fields["any"] = any_filter
            if any_filter:
                filtered_resources = (
                        filtered_resources.filter(title__icontains=any_filter) |
                        filter_by_author_name(filtered_resources, any_filter) |
                        filter_by_year_str(filtered_resources, any_filter) |
                        filtered_resources.filter(summary__icontains=any_filter)
                ).distinct()

            title_filter = request.GET.get("title", None)
            form_fields["title"] = title_filter
            if title_filter:
                filtered_resources = filtered_resources.filter(title__icontains=title_filter)

            author_filter = request.GET.get("author", None)
            form_fields["author"] = author_filter
            if author_filter:
                filtered_resources = filter_by_author_name(filtered_resources, author_filter).distinct()

            year_filter = request.GET.get("year", None)
            form_fields["year"] = year_filter
            if year_filter:
                filtered_resources = filtered_resources.filter(year=year_filter)

            title_filter = request.GET.get("summary", None)
            form_fields["summary"] = title_filter
            if title_filter:
                filtered_resources = filtered_resources.filter(summary__icontains=title_filter)

    context = {
        "resources": filtered_resources,
        "form_fields": form_fields,
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

            messages.success(request, f'Resource {resource} created successfully.')

    return redirect("myapp:resources")


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
            # Filter results using form
            any_filter = request.GET.get("any", None)
            form_fields["any"] = any_filter
            if any_filter:
                filtered_scenarios = (
                        filtered_scenarios.filter(name__icontains=any_filter) |
                        filtered_scenarios.filter(
                            subject=
                            get_choice_from_label_icontains(Subjects, any_filter)
                        ) |
                        filtered_scenarios.filter(
                            age_group=
                            get_choice_from_label_icontains(AgeGroups, any_filter)
                        ) |
                        filtered_scenarios.filter(outcomes__name__icontains=any_filter)
                ).distinct()

            name_filter = request.GET.get("name", None)
            form_fields["name"] = name_filter
            if name_filter:
                filtered_scenarios = filtered_scenarios.filter(name__icontains=name_filter)

            subject_filter = request.GET.get("subject", None)
            form_fields["subject"] = subject_filter
            if subject_filter:
                subject_filter = get_choice_from_label(Subjects, subject_filter)
                filtered_scenarios = filtered_scenarios.filter(subject=subject_filter)

            age_group_filter = request.GET.get("age_group", None)
            form_fields["age_group"] = age_group_filter
            if age_group_filter:
                age_group_filter = get_choice_from_label(AgeGroups, age_group_filter)
                filtered_scenarios = filtered_scenarios.filter(age_group=age_group_filter)

            outcome_filter = request.GET.get("outcome", None)
            form_fields["outcome"] = outcome_filter
            if outcome_filter:
                filtered_scenarios = filtered_scenarios.filter(outcomes__name__icontains=outcome_filter)

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
