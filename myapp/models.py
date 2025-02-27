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
    """Describe which authors wrote which resources."""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ["resource", "order"]
        ordering = ["resource__title", "order"]

    def __str__(self):
        return f"{self.resource.get_short_title()}, {self.author}, {self.order}"
