"""
Element views for myapp application.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from myapp.models import Element
from .viewutils import filter_elements


def elements(request) -> HttpResponse:
    filtered_elements = Element.objects.all()
    form_fields = {}

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            filtered_elements = filter_elements(
                request, filtered_elements, form_fields
            )

    context = {
        "elements": filtered_elements,
        "form_fields": form_fields,
    }
    return render(
        request,
        "myapp/elements.html",
        context
    )


def element_view(request, element_pk: int) -> HttpResponse:
    element = get_object_or_404(Element, pk=element_pk)

    context = {
        "element": element
    }
    return render(
        request,
        "myapp/element_view.html",
        context
    )


def add_element(request) -> HttpResponse:
    return render(
        request,
        "myapp/add_element.html"
    )


def add_element_form(request) -> HttpResponse:
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "add_element":
            # Add element
            name = request.POST.get("name")
            description = request.POST.get("description")
            existing_element = Element.objects.filter(name=name)
            if existing_element.exists():
                # Element already exists
                messages.error(request, "An element with that name already exists.")
                return redirect("myapp:elements")

            element = Element.objects.create(
                name=name, description=description
            )

            messages.success(request, f'Element {element} created successfully.')

    return redirect("myapp:elements")