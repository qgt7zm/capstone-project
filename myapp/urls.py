"""
URL configuration for myapp application.
"""

from django.urls import path

from . import dataviews, resourceviews, resultviews, scenarioviews, views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("elements", views.elements, name="elements"),
    path("outcomes", views.outcomes, name="outcomes"),
    path("resources", resourceviews.resources, name="resources"),
    path("resources/<int:resource_pk>", resourceviews.resource_view, name="resource_view"),
    path("resources/add", resourceviews.add_resource, name="add_resource"),
    path("resources/add/form", resourceviews.add_resource_form, name="add_resource_form"),
    path("resources/<int:resource_pk>/add_result", resultviews.add_result, name="add_result"),
    path("resources/<int:resource_pk>/add_result/form", resultviews.add_result_form, name="add_result_form"),
    path("scenarios", scenarioviews.scenarios, name="scenarios"),
    path("scenarios/<int:scenario_pk>", scenarioviews.scenario_view, name="scenario_view"),
    path("scenarios/add", scenarioviews.add_scenario, name="add_scenario"),
    path("scenarios/add/form", scenarioviews.add_scenario_form, name="add_scenario_form"),
    path("data", views.data, name="data"),
    path("data/export", dataviews.data_export, name="data_export"),
    path("data/upload", dataviews.data_upload, name="data_upload"),
    path("data/delete", dataviews.data_delete, name="data_delete"),
    path("about", views.about, name="about"),
]
