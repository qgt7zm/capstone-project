"""
Helper methods for myapp models.

See also:

- https://docs.djangoproject.com/en/5.1/ref/models/expressions/
- https://docs.djangoproject.com/en/5.1/topics/db/aggregation/
"""

from django.db import models
from django.db.models import QuerySet
from django.db.models.functions import Cast

from myapp.models import Resource, Outcome, Element, Result


# Choice Helper Methods


def get_choice_from_label(choices_cls: type, choice_label: str) -> models.IntegerChoices | None:
    """Filter choices by label name."""
    for val, label in choices_cls.choices:
        if label == choice_label:
            return val
    return None


def get_choice_from_label_icontains(choices_cls: type, choice_label: str) -> models.IntegerChoices | int:
    """Filter choices by label contains."""
    for val, label in choices_cls.choices:
        if choice_label.lower() in label.lower():
            return val
    return -1


# Model Helper Methods

def filter_by_author_name(resources: QuerySet[Resource], author_name: str) -> QuerySet[Resource]:
    """Filter resources by author name."""
    return (
            resources.filter(authors__first_name__icontains=author_name) |
            resources.filter(authors__last_name__icontains=author_name)
    )


def filter_by_year_str(resources: QuerySet[Resource], year: str) -> QuerySet[Resource]:
    """Filter resources by year string."""
    cast_resources = resources.annotate(
        year_str=Cast("year", output_field=models.CharField(max_length=100))
    )
    return cast_resources.filter(year_str=year)


def filter_by_element_name(elements: QuerySet[Outcome], element_name: str) -> QuerySet[Outcome]:
    """Filter outcomes by element name."""
    element_pks = Element.objects.filter(name__icontains=element_name).values("pk")
    element_results = Result.objects.filter(elements__in=element_pks)
    outcome_pks = element_results.values("outcomes").distinct()
    return elements.filter(pk__in=outcome_pks)


def filter_by_outcome_name(outcomes: QuerySet[Element], outcome_name: str) -> QuerySet[Element]:
    """Filter elements by outcome name."""
    outcome_pks = Outcome.objects.filter(name__icontains=outcome_name).values("pk")
    outcome_results = Result.objects.filter(outcomes__in=outcome_pks)
    element_pks = outcome_results.values("elements").distinct()
    return outcomes.filter(pk__in=element_pks)


def filter_by_resource_citation(
        objects: QuerySet[Element | Outcome], citation: str, model_name: str
) -> QuerySet[Element | Outcome]:
    """Filter outcomes by resource authors and year."""
    filtered_resources = Resource.objects.all()
    filtered_resources = (
            filter_by_author_name(filtered_resources, citation) |
            filter_by_year_str(filtered_resources, citation)
    )
    resource_results = Result.objects.filter(resource__in=filtered_resources)
    outcome_pks = resource_results.values(model_name).distinct()
    return objects.filter(pk__in=outcome_pks)
