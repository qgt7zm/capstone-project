"""
Element views for myapp application.
"""
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

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
