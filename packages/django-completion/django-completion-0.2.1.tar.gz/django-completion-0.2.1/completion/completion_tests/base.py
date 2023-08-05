from django.test import TestCase

from completion.completion_tests.models import Blog, Note1, Note2, Note3


class AutocompleteTestCase(TestCase):
    fixtures = ['completion_testdata.json']
    
    def setUp(self):
        self.blog_tp = Blog.objects.get(pk=1)
        self.blog_tpc = Blog.objects.get(pk=2)
        self.blog_wtp = Blog.objects.get(pk=3)
        self.blog_utp = Blog.objects.get(pk=4)
        self.blog_unpub = Blog.objects.get(pk=5)
    
    def create_notes(self):
        notes = []
        for i in range(3):
            for klass in [Note1, Note2, Note3]:
                title = 'note class-%s number-%s' % (klass._meta.module_name, i)
                notes.append(klass.objects.create(title=title))
        return notes


class AutocompleteBackendTestCase(object):
    def test_suggest(self):
        test_site = self.test_site
        
        test_site.store_providers()
        
        results = test_site.suggest('testing python')
        self.assertEqual(sorted(results), [
            {'stored_title': 'testing python'},
            {'stored_title': 'testing python code'},
            {'stored_title': 'web testing python code'},
        ])
        
        results = test_site.suggest('test')
        self.assertEqual(sorted(results), [
            {'stored_title': 'testing python'},
            {'stored_title': 'testing python code'},
            {'stored_title': 'unit tests with python'},
            {'stored_title': 'web testing python code'},
        ])
        
        results = test_site.suggest('unit')
        self.assertEqual(results, [{'stored_title': 'unit tests with python'}])
        
        results = test_site.suggest('')
        self.assertEqual(results, [])
        
        results = test_site.suggest('another')
        self.assertEqual(results, [])
    
    def test_removing_objects(self):
        test_site = self.test_site
        
        test_site.store_providers()
        
        test_site.remove_object(self.blog_tp)
        
        results = test_site.suggest('testing')
        self.assertEqual(sorted(results), [
            {'stored_title': 'testing python code'}, 
            {'stored_title': 'web testing python code'},
        ])
        
        test_site.store_object(self.blog_tp)
        test_site.remove_object(self.blog_tpc)
        
        results = test_site.suggest('testing')
        self.assertEqual(sorted(results), [
            {'stored_title': 'testing python'}, 
            {'stored_title': 'web testing python code'},
        ])
    
    def test_filtering_by_type(self):
        test_site = self.test_site
        
        for note in self.create_notes():
            test_site.store_object(note)
        
        # first check that our results are as expected
        results = test_site.suggest('note')
        self.assertEqual(sorted(results), [
            {u'stored_title': u'note class-note1 number-0'},
            {u'stored_title': u'note class-note1 number-1'},
            {u'stored_title': u'note class-note1 number-2'},
            {u'stored_title': u'note class-note2 number-0'}, 
            {u'stored_title': u'note class-note2 number-1'}, 
            {u'stored_title': u'note class-note2 number-2'}, 
            {u'stored_title': u'note class-note3 number-0'}, 
            {u'stored_title': u'note class-note3 number-1'}, 
            {u'stored_title': u'note class-note3 number-2'}
        ])
        
        results = test_site.suggest('note', models=[Note1])
        self.assertEqual(sorted(results), [
            {u'stored_title': u'note class-note1 number-0'},
            {u'stored_title': u'note class-note1 number-1'},
            {u'stored_title': u'note class-note1 number-2'},
        ])
        
        results = test_site.suggest('note', models=[Note1, Note3])
        self.assertEqual(sorted(results), [
            {u'stored_title': u'note class-note1 number-0'},
            {u'stored_title': u'note class-note1 number-1'},
            {u'stored_title': u'note class-note1 number-2'},
            {u'stored_title': u'note class-note3 number-0'}, 
            {u'stored_title': u'note class-note3 number-1'}, 
            {u'stored_title': u'note class-note3 number-2'}
        ])
