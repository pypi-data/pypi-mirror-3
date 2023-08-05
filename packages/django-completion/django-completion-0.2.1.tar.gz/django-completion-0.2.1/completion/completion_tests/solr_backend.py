from django.contrib.auth.models import User

from completion.backends.solr_backend import SolrAutocomplete
from completion.completion_tests.base import AutocompleteTestCase, AutocompleteBackendTestCase
from completion.completion_tests.models import Blog, Note1, Note2, Note3, BlogProvider, NoteProvider
from completion.sites import AutocompleteSite


test_site = AutocompleteSite(SolrAutocomplete())
test_site.register(Blog, BlogProvider)
test_site.register(Note1, NoteProvider)
test_site.register(Note2, NoteProvider)
test_site.register(Note3, NoteProvider)


class SolrBackendTestCase(AutocompleteTestCase, AutocompleteBackendTestCase):
    def setUp(self):
        self.test_site = test_site
        AutocompleteTestCase.setUp(self)
