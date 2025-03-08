"""
Models for myapp application.

See also: https://docs.djangoproject.com/en/5.1/ref/models/querysets/
"""

from django.db import models


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

    def __str__(self) -> str:
        return f"{self.get_short_title()} {self.get_citation()}"

    def get_short_title(self, max_length: int = 40) -> str:
        title = str(self.title)
        if len(title) <= max_length:
            return title
        else:
            return title[:max_length] + "..."

    def get_authors(self) -> list[Author]:
        return list(Author.objects.prefetch_related("resourceauthor_set")
                    .filter(resourceauthor__resource=self)
                    .order_by("resourceauthor__order"))

    def get_citation(self) -> str:
        authors = self.get_authors()
        if len(authors) == 0:
            authors_str = f'"{self.title}"'
        elif len(authors) == 1:
            authors_str = authors[0].last_name
        elif len(authors) == 2:
            authors_str = f"{authors[0].last_name} & {authors[1].last_name}"
        else:
            authors_str = f"{authors[0].last_name} et al."

        return f"({authors_str}, {self.year})"


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

    def __str__(self):
        return str(self.name)


class Outcome(models.Model):
    """A student learning outcome."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

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

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    elements = models.ManyToManyField(Element, related_name="results")
    outcomes = models.ManyToManyField(Outcome, related_name="results")
    rating = models.IntegerField(choices=ResultRatings)
    age_group = models.IntegerField(choices=AgeGroups)
    sample_size = models.PositiveIntegerField()

    class Meta:
        ordering = ["resource__title"]

    def __str__(self):
        return f"{self.resource.get_citation()} result, {self.rating}, {self.age_group}, {self.sample_size}"


model_classes = [
    Author,
    Resource,
    ResourceAuthor,
    Element,
    Outcome,
    Result,
]
