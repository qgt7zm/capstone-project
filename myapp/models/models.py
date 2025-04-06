"""
Model classes for myapp application.

See also:

- https://docs.djangoproject.com/en/5.1/ref/models/querysets/
"""

from django.db import models
from django.db.models import QuerySet, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .modelenums import ResultRatings, AgeGroups, Subjects

# Constants

MAX_PREVIEW_AUTHORS = 4


# Model Classes

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

    def get_authors(self) -> QuerySet[Author]:
        return (
            Author.objects.prefetch_related("resourceauthor_set")
            .filter(resourceauthor__resource=self)
            .order_by("resourceauthor__order")
        )

    def get_short_authors(self) -> list[str]:
        authors = [str(author) for author in self.get_authors()]
        num_authors = len(authors)
        if num_authors > MAX_PREVIEW_AUTHORS:
            authors = authors[:MAX_PREVIEW_AUTHORS - 1]
            authors.append(f"+ {num_authors - (MAX_PREVIEW_AUTHORS - 1)} more")
        return authors

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

    def get_results(self) -> QuerySet['Result']:
        return Result.objects.filter(resource=self)

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
        return str(ResultRatings(self.rating).label)

    def get_subject(self) -> str:
        return str(Subjects(self.subject).label)

    def get_age_group(self) -> str:
        return str(AgeGroups(self.age_group).label)

    def __str__(self):
        return (f"{self.resource.get_citation()}, {self.get_rating()}, "
                f"{self.get_subject()}, {self.get_age_group()}, {self.sample_size}")


class Scenario(models.Model):
    """A gamified classroom plan with needs and recommendations."""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    outcomes = models.ManyToManyField(Outcome)
    subject = models.IntegerField(choices=Subjects, null=True, blank=True)
    age_group = models.IntegerField(choices=AgeGroups, null=True, blank=True)

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
        return str(Subjects(self.subject).label)

    def get_age_group(self) -> str:
        if self.age_group is None:
            return "N/A"
        return str(AgeGroups(self.age_group).label)

    def __str__(self):
        return f"{self.name}"


# Model Helper Methods

# Can't move due to circular import
def order_by_citation(resources: QuerySet[Resource]) -> QuerySet[Resource]:
    """Sort resources by last name of first author."""
    author1_last_name = ResourceAuthor.objects.filter(
        resource=OuterRef("pk"), order=0
    ).values("author__last_name")
    return resources.annotate(
        author1__last_name=Coalesce(
            Subquery(author1_last_name), Value("")
        )
    ).order_by("author1__last_name", "year")
