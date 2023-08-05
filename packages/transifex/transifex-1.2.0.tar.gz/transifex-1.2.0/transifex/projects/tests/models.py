# -*- coding: utf-8 -*-
from django.db import IntegrityError
from transifex.txcommon.tests.base import BaseTestCase
from transifex.languages.models import Language
from transifex.resources.models import Translation
from transifex.projects.models import Project
from transifex.resources.models import Resource


class ModelTests(BaseTestCase):

    def setUp(self):
        super(ModelTests, self).setUp()

    def tearDown(self):
        super(ModelTests, self).tearDown()

    def test_project_slug_integrity(self):
        """ Check duplication of project slug."""
        p, created = Project.objects.get_or_create(
            slug="foo", name="Foo Project", source_language=self.language_en
        )
        new_p = Project(
            slug="foo", name="Foo Project", source_language = self.language_en
        )
        self.assertRaises(IntegrityError, new_p.save)

    def test_def_manager_public(self):
        """Test that managers behave the same between models and relations.

        Grab a maintainer's public projects through the model and compare them
        with the ones returned from his own instance's foreign key relation.
        """
        self.assertEqual(
            Project.objects.filter(maintainers__id=self.user['maintainer'].pk).public().count(),
            self.user['maintainer'].projects_maintaining.filter(private=False).count(),)

    def test_project_resource_source_lang(self):
        """Test the source_language field against a resource."""
        p = Project.objects.create(slug='slug', source_language=self.language_en)
        self.assertEquals(p.source_language, self.language_en)
        r = Resource.objects.create(
            slug='rslug', project=p, source_language=self.language_ar
        )
        self.assertEqual(r.source_language, p.source_language)
