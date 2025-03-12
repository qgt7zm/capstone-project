"""
Tests for myapp application.
"""

from django.test import TestCase

from .models import *


class ResourceTest(TestCase):
    def test_resource_get_authors_none(self):
        Author.objects.create(first_name="A", last_name="Aaa")
        Author.objects.create(first_name="B", last_name="Bbb")

        resource1 = Resource.objects.create(year=2025)

        self.assertEqual([], list(resource1.get_authors()))


    def test_resource_get_authors_single(self):
        author1 = Author.objects.create(first_name="A", last_name="Aaa")
        Author.objects.create(first_name="B", last_name="Bbb")

        resource1 = Resource.objects.create(title="1", year=2025)
        ResourceAuthor.objects.create(resource=resource1, author=author1, order=0)

        self.assertEqual([author1], list(resource1.get_authors()))


    def test_resource_get_authors_multiple(self):
        author1 = Author.objects.create(first_name="A", last_name="Aaa")
        author2 = Author.objects.create(first_name="B", last_name="Bbb")

        resource1 = Resource.objects.create(title="1", year=2025)
        ResourceAuthor.objects.create(resource=resource1, author=author1, order=0)
        ResourceAuthor.objects.create(resource=resource1, author=author2, order=1)

        self.assertEqual([author1, author2], list(resource1.get_authors()))
