"""
URL configuration for myapp application.
"""

from django.urls import path

from myapp import views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("about", views.about, name="about"),

    path("elements", views.elements, name="elements"),
    path("elements/<int:element_pk>", views.element_view, name="element_view"),
    path("elements/add", views.add_element, name="add_element"),
    path("elements/add/form", views.add_element_form, name="add_element_form"),
    path("elements/<int:element_pk>/edit", views.edit_element, name="edit_element"),
    path("elements/<int:element_pk>/edit/form", views.edit_element_form, name="edit_element_form"),
    path("elements/<int:element_pk>/delete", views.delete_element, name="delete_element"),

    path("outcomes", views.outcomes, name="outcomes"),
    path("outcomes/<int:outcome_pk>", views.outcome_view, name="outcome_view"),
    path("outcomes/add", views.add_outcome, name="add_outcome"),
    path("outcomes/add/form", views.add_outcome_form, name="add_outcome_form"),
    path("outcomes/<int:outcome_pk>/edit", views.edit_outcome, name="edit_outcome"),
    path("outcomes/<int:outcome_pk>/edit/form", views.edit_outcome_form, name="edit_outcome_form"),
    path("outcomes/<int:outcome_pk>/delete", views.delete_outcome, name="delete_outcome"),

    path("resources", views.resources, name="resources"),
    path("resources/<int:resource_pk>", views.resource_view, name="resource_view"),
    path("resources/add", views.add_resource, name="add_resource"),
    path("resources/add/form", views.add_resource_form, name="add_resource_form"),
    path("resources/<int:resource_pk>/edit", views.edit_resource, name="edit_resource"),
    path("resources/<int:resource_pk>/edit/form", views.edit_resource_form, name="edit_resource_form"),
    path("resources/<int:resource_pk>/add_result", views.add_result, name="add_result"),
    path("resources/<int:resource_pk>/add_result/form", views.add_result_form, name="add_result_form"),
    path("resources/<int:resource_pk>/delete", views.delete_resource, name="delete_resource"),
    path("resources/<int:resource_pk>/clear_results", views.clear_results, name="clear_results"),

    path("scenarios", views.scenarios, name="scenarios"),
    path("scenarios/<int:scenario_pk>", views.scenario_view, name="scenario_view"),
    path("scenarios/add", views.add_scenario, name="add_scenario"),
    path("scenarios/add/form", views.add_scenario_form, name="add_scenario_form"),
    path("scenarios/<int:scenario_pk>/edit", views.edit_scenario, name="edit_scenario"),
    path("scenarios/<int:scenario_pk>/edit/form", views.edit_scenario_form, name="edit_scenario_form"),
    path("scenarios/<int:scenario_pk>/delete", views.delete_scenario, name="delete_scenario"),

    path("data", views.data, name="data"),
    path("data/export", views.data_export, name="data_export"),
    path("data/upload", views.data_upload, name="data_upload"),
    path("data/delete", views.data_delete, name="data_delete"),
]
