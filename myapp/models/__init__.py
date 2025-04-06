"""
Views for myapp application.
"""
from .models import *
from .modelenums import *
from .modelutils import *

# Define model classes for serialization
model_classes = [
    Author,
    Resource,
    ResourceAuthor,
    Element,
    Outcome,
    Result,
    Scenario,
]
