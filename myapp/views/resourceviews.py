"""
Resource views for myapp application.
"""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from myapp.models import order_by_citation, Resource, Result, Author, ResourceAuthor
from .viewutils import filter_resources


def resources(request) -> HttpResponse:
    filtered_resources = order_by_citation(Resource.objects.all())
    form_fields = {}

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "search":
            filtered_resources = filter_resources(
                request, filtered_resources, form_fields
            )

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

    context = {
        "resource": resource,
        "results": resource.get_results(),
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
