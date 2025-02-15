"""
Views for myapp application.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


def index(request) -> HttpResponse:
    return HttpResponseRedirect(reverse("myapp:home"))

def home(request):
    return HttpResponse("You've reached the homepage.")
