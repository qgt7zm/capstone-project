"""
Helper methods for myapp views.
"""
from myapp.models import *


def filter_elements(request, filtered_elements, form_fields):
    """Filter elements shown using search form."""
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

    return filtered_elements


def filter_outcomes(request, filtered_outcomes, form_fields):
    """Filter outcomes shown using search form."""
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

    return filtered_outcomes


def filter_resources(request, filtered_resources, form_fields):
    """Filter results shown using search form."""
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

    return filtered_resources


def filter_scenarios(request, filtered_scenarios, form_fields):
    """Filter scenarios shown using search form."""
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

    return filtered_scenarios
