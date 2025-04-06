"""
Model enums for myapp application.
"""
from django.db import models


class ResultRatings(models.IntegerChoices):
    VERY_POSITIVE = 2, "Very Positive"
    SOMEWHAT_POSITIVE = 1, "Somewhat Positive"
    NEUTRAL = 0, "Neutral"
    SOMEWHAT_NEGATIVE = -1, "Somewhat Negative"
    VERY_NEGATIVE = -2, "Very Negative"


class AgeGroups(models.IntegerChoices):
    ELEMENTARY = 0, "Elementary School (K-5)"
    MIDDLE = 1, "Middle School (6-8)"
    HIGH = 2, "High School (9-12)"
    UNDERGRAD = 3, "Undergraduate"
    GRADUATE = 4, "Graduate"
    OTHER = 5, "Other"


class Subjects(models.IntegerChoices):
    COMPUTING = 0, "Computing"
    ENGINEERING = 1, "Engineering"
    MATH = 2, "Mathematics"
    SCIENCE = 3, "Sciences"
    MEDICINE = 4, "Medicine"
    LANGUAGE = 5, "Languages"
    HUMANITIES = 6, "Humanities"
    OTHER = 10, "Other"
