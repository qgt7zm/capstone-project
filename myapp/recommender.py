"""
Recommendation algorithm for myapp application.
"""
from math import sqrt

from django.db import models
from django.db.models import Count, Avg, Case, When, Value, Q

from myapp.models import Element, Resource, Result, order_by_citation


def get_recommendations_individual(scenario):
    """Recommend elements for each outcome"""
    scenario_outcomes = scenario.get_outcomes()
    recommendations = {}
    for outcome in scenario_outcomes:
        print(outcome)
        outcome_recommendations = {}

        # Get resources and  results for outcome
        outcome_results = Result.objects.none()
        outcome_resources = outcome.get_resources()
        for resource in outcome_resources:
            resource_results = Result.objects.filter(resource=resource).all()
            outcome_results |= resource_results

        outcome_resources = order_by_citation(outcome_resources)
        outcome_recommendations["resources"] = outcome_resources
        outcome_results = outcome_results.annotate(count_elements=Count("elements"))

        # Get elements for outcome
        element_pks = outcome_results.values("elements").distinct()
        outcome_elements = Element.objects.filter(pk__in=element_pks)

        # Get results and score for element
        element_scores = []
        for element in outcome_elements:
            element_results = outcome_results.filter(pk__in=element.results.values("pk"))

            # Evaluate element score
            aggregation = element_results.aggregate(
                avg_rating=Avg("rating", default=Result.ResultRatings.NEUTRAL.value),
                count_results=Count("pk"),
                avg_count_elements=Avg("count_elements"),
                subject_similarity=Avg(Case(
                    When(subject=scenario.subject, then=Value(1.1)),
                    default=Value(0.9),
                    output_field=models.IntegerField()
                )),
                age_group_similarity=Avg(Case(
                    When(age_group=scenario.age_group, then=Value(1.1)),
                    default=Value(0.9),
                    output_field=models.IntegerField()
                )),
            )

            element_score = (
                    aggregation["avg_rating"] *
                    sqrt(aggregation["count_results"]) /
                    sqrt(aggregation["avg_count_elements"]) *
                    aggregation["subject_similarity"] * aggregation["age_group_similarity"]
            )
            element_score = round(element_score, 2)

            element_scores.append({
                "name": element,
                "score": element_score,
            })
            element_scores.sort(key=lambda x: x["score"], reverse=True)

        outcome_recommendations["elements"] = element_scores
        recommendations[outcome.name] = outcome_recommendations

    return recommendations


def get_recommendations_combined(scenario):
    """Recommend elements for all outcomes."""
    scenario_outcomes = scenario.get_outcomes()
    recommendations = {}

    # Get all results for outcomes
    scenario_results = Result.objects.none()
    for outcome in scenario_outcomes:
        outcome_resources = outcome.get_resources()
        for resource in outcome_resources:
            resource_results = Result.objects.filter(resource=resource).all()
            scenario_results |= resource_results
        outcome_resources = order_by_citation(outcome_resources)
        recommendations["resources"] = outcome_resources

    scenario_results = scenario_results.annotate(
        count_elements=Count("elements"),
        count_outcomes_desired=Count("outcomes", filter=Q(
            outcomes__in=scenario.outcomes.all()
        )),
    )
    for result in scenario_results:
        print(result.outcomes.all(), result.count_outcomes_desired)

    # Get resources for all outcomes
    resource_pks = scenario_results.values("resource").distinct()
    scenario_resources = Resource.objects.filter(pk__in=resource_pks)
    recommendations["resources"] = scenario_resources

    # Get elements for all results
    element_pks = scenario_results.values("elements").distinct()
    scenario_elements = Element.objects.filter(pk__in=element_pks)

    # Get results and score for element
    element_scores = []
    for element in scenario_elements:
        element_results = scenario_results.filter(pk__in=element.results.values("pk"))

        # Evaluate element score
        aggregation = element_results.aggregate(
            avg_rating=Avg("rating", default=Result.ResultRatings.NEUTRAL.value),
            count_results=Count("pk"),
            prop_outcomes_desired = scenario.outcomes.count() / Avg("count_outcomes_desired"),
            avg_count_elements=Avg("count_elements"),
            subject_similarity=Avg(Case(
                When(subject=scenario.subject, then=Value(1.1)),
                default=Value(0.9),
                output_field=models.IntegerField()
            )),
            age_group_similarity=Avg(Case(
                When(age_group=scenario.age_group, then=Value(1.1)),
                default=Value(0.9),
                output_field=models.IntegerField()
            )),
        )
        print(aggregation)

        element_score = (
                aggregation["avg_rating"] *
                sqrt(aggregation["count_results"]) /
                sqrt(aggregation["avg_count_elements"]) *
                sqrt(aggregation["prop_outcomes_desired"]) *
                aggregation["subject_similarity"] * aggregation["age_group_similarity"]
        )
        element_score = round(element_score, 2)

        element_scores.append({
            "name": element,
            "score": element_score,
        })
        element_scores.sort(key=lambda x: x["score"], reverse=True)

    recommendations["elements"] = element_scores
    return recommendations
