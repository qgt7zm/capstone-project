"""
Models for myapp application.

See also:

- https://docs.djangoproject.com/en/5.1/ref/models/querysets/
- https://docs.djangoproject.com/en/5.1/ref/models/expressions/
- https://docs.djangoproject.com/en/5.1/topics/db/aggregation/
"""

from django.db import models
from django.db.models import QuerySet, OuterRef, Subquery, Value
from django.db.models.functions import Cast, Coalesce


class Author(models.Model):
    """A subject-matter expert."""
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Resource(models.Model):
    """A journal article, website, or book written."""
    title = models.CharField(max_length=300)
    authors = models.ManyToManyField(Author, through="ResourceAuthor", related_name="resources")
    year = models.IntegerField()
    publisher = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=400, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["title"]

    def get_short_title(self, max_length: int = 40) -> str:
        title = str(self.title)
        if len(title) <= max_length:
            return title
        else:
            return title[:max_length] + "..."

    def get_authors(self) -> QuerySet:
        return (
            Author.objects.prefetch_related("resourceauthor_set")
            .filter(resourceauthor__resource=self)
            .order_by("resourceauthor__order")
        )

    def get_citation(self) -> str:
        authors = self.get_authors()
        if len(authors) == 0:
            authors_str = f'"{self.get_short_title()}"'
        elif len(authors) == 1:
            authors_str = authors[0].last_name
        elif len(authors) == 2:
            authors_str = f"{authors[0].last_name} & {authors[1].last_name}"
        else:
            authors_str = f"{authors[0].last_name} et al."

        return f"({authors_str}, {self.year})"

    def __str__(self) -> str:
        return f"{self.get_short_title()} {self.get_citation()}"


class ResourceAuthor(models.Model):
    """Describes which authors wrote which resources."""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ["resource", "order"]
        ordering = ["resource__title", "order"]

    def __str__(self):
        return f"{self.resource.get_short_title()}, {self.author}, {self.order}"


class Element(models.Model):
    """A game element or mechanic."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def get_outcomes(self) -> QuerySet['Outcome']:
        outcome_pks = (
            Result.objects.filter(elements__in=[self])
            .values("outcomes").distinct()
        )
        return Outcome.objects.filter(pk__in=outcome_pks)

    def get_resources(self) -> QuerySet[Resource]:
        resource_pks = (
            Result.objects.filter(elements__in=[self])
            .values("resource").distinct()
        )
        return order_by_citation(Resource.objects.filter(pk__in=resource_pks))

    def __str__(self):
        return str(self.name)


class Outcome(models.Model):
    """A student learning outcome."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def get_elements(self) -> QuerySet[Element]:
        element_pks = (
            Result.objects.filter(outcomes__in=[self])
            .values("elements").distinct()
        )
        return Element.objects.filter(pk__in=element_pks)

    def get_resources(self) -> QuerySet[Resource]:
        resource_pks = (
            Result.objects.filter(outcomes__in=[self])
            .values("resource").distinct()
        )
        return order_by_citation(Resource.objects.filter(pk__in=resource_pks))

    def __str__(self):
        return str(self.name)


class Result(models.Model):
    """The result of a gamification study."""

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

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    elements = models.ManyToManyField(Element, related_name="results")
    outcomes = models.ManyToManyField(Outcome, related_name="results")
    rating = models.IntegerField(choices=ResultRatings)
    subject = models.IntegerField(choices=Subjects)
    age_group = models.IntegerField(choices=AgeGroups)
    sample_size = models.PositiveIntegerField()

    class Meta:
        ordering = ["resource__title"]

    def get_elements(self) -> str:
        return ", ".join([element.name for element in self.elements.all()])

    def get_outcomes(self) -> str:
        return ", ".join([outcomes.name for outcomes in self.outcomes.all()])

    def get_rating(self) -> str:
        return str(Result.ResultRatings(self.rating).label)

    def get_subject(self) -> str:
        return str(Result.Subjects(self.subject).label)

    def get_age_group(self) -> str:
        return str(Result.AgeGroups(self.age_group).label)

    def __str__(self):
        return (f"{self.resource.get_citation()}, {self.get_rating()}, "
                f"{self.get_subject()}, {self.get_age_group()}, {self.sample_size}")


class Scenario(models.Model):
    """A gamified classroom plan with needs and recommendations."""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    outcomes = models.ManyToManyField(Outcome)
    subject = models.IntegerField(choices=Result.Subjects, null=True, blank=True)
    age_group = models.IntegerField(choices=Result.AgeGroups, null=True, blank=True)

    class Meta:
        unique_together = ["name"]
        ordering = ["created_at", "name"]

    def get_created_at(self) -> str:
        return self.created_at.strftime("%b %d, %Y, %H:%M %p")

    def get_outcomes(self) -> QuerySet[Outcome]:
        return self.outcomes.all()

    def get_subject(self) -> str:
        if self.subject is None:
            return "N/A"
        return str(Result.Subjects(self.subject).label)

    def get_age_group(self) -> str:
        if self.age_group is None:
            return "N/A"
        return str(Result.AgeGroups(self.age_group).label)

    def __str__(self):
        return f"{self.name}"


model_classes = [
    Author,
    Resource,
    ResourceAuthor,
    Element,
    Outcome,
    Result,
    Scenario,
]


# Model Helper Methods

def get_choice_from_label(choices_cls: type, choice_label: str) -> models.IntegerChoices | None:
    for val, label in choices_cls.choices:
        if label == choice_label:
            return val
    return None


def get_choice_from_label_icontains(choices_cls: type, choice_label: str) -> models.IntegerChoices | int:
    for val, label in choices_cls.choices:
        if choice_label.lower() in label.lower():
            return val
    return -1


def order_by_citation(resources: QuerySet[Resource]) -> QuerySet[Resource]:
    # Sort by last name of first author
    author1_last_name = ResourceAuthor.objects.filter(
        resource=OuterRef("pk"), order=0
    ).values("author__last_name")
    return resources.annotate(
        author1__last_name=Coalesce(
            Subquery(author1_last_name), Value("")
        )
    ).order_by("author1__last_name", "year")


def filter_by_author_name(resources: QuerySet[Resource], author_name: str) -> QuerySet[Resource]:
    # Filter resources by author name
    return (
            resources.filter(authors__first_name__icontains=author_name) |
            resources.filter(authors__last_name__icontains=author_name)
    )


def filter_by_year_str(resources: QuerySet[Resource], year: str) -> QuerySet[Resource]:
    # Filter resources by year string
    cast_resources = resources.annotate(
        year_str=Cast("year", output_field=models.CharField(max_length=100))
    )
    return cast_resources.filter(year_str=year)


def filter_by_element_name(elements: QuerySet[Outcome], element_name: str) -> QuerySet[Outcome]:
    # Filter outcomes by element name
    element_pks = Element.objects.filter(name__icontains=element_name).values("pk")
    element_results = Result.objects.filter(elements__in=element_pks)
    outcome_pks = element_results.values("outcomes").distinct()
    return elements.filter(pk__in=outcome_pks)


def filter_by_outcome_name(outcomes: QuerySet[Element], outcome_name: str) -> QuerySet[Element]:
    # Filter elements by outcome name
    outcome_pks = Outcome.objects.filter(name__icontains=outcome_name).values("pk")
    outcome_results = Result.objects.filter(outcomes__in=outcome_pks)
    element_pks = outcome_results.values("elements").distinct()
    return outcomes.filter(pk__in=element_pks)


def filter_by_resource_citation(
        objects: QuerySet[Element | Outcome], citation: str, model_name: str
) -> QuerySet[Element | Outcome]:
    # Filter outcomes by resource authors and year
    filtered_resources = Resource.objects.all()
    filtered_resources = (
            filter_by_author_name(filtered_resources, citation) |
            filter_by_year_str(filtered_resources, citation)
    )
    resource_results = Result.objects.filter(resource__in=filtered_resources)
    outcome_pks = resource_results.values(model_name).distinct()
    return objects.filter(pk__in=outcome_pks)
