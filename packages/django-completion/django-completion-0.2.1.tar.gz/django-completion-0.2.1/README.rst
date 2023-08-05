=================
django-completion
=================

autocompletion for django apps

supports the following backends:

* solr
* database (using LIKE)
* redis (pretty experimental)

usage follows typical django registration-y pattern::

    from django.db import models

    from completion import site


    class Blog(models.Model):
        title = models.CharField(max_length=255)
        pub_date = models.DateTimeField()
        content = models.TextField()
        published = models.BooleanField(default=True)

        def get_absolute_url(self):
            return reverse('blog_detail', args=[self.pk])


    class BlogProvider(AutocompleteProvider):
        def get_title(self, obj):
            return obj.title

        def get_pub_date(self, obj):
            return datetime.datetime(2010, 1, 1)

        def get_data(self, obj):
            return {'stored_title': obj.title, 'url': obj.get_absolute_url()}

        def get_queryset(self):
            return self.model._default_manager.filter(published=True)


    site.register(Blog, BlogProvider)


The Blog model is now ready for autocomplete, but the objects must be stored before they can be returned::

    >>> from completion import site
    >>> site.store_providers()
    >>> site.suggest('tes')
    [
        {u'stored_title': u'testing python', u'url': u'/blogs/1/'},
        {u'stored_title': u'testing python code', u'url': u'/blogs/3/'},
        {u'stored_title': u'web testing python', u'url': u'/blogs/2/'},
        {u'stored_title': u'unit tests with python', u'url': u'/blogs/4/'},
    ]

    >>> site.suggest('testing')
    [
        {u'stored_title': u'testing python', u'url': u'/blogs/1/'},
        {u'stored_title': u'testing python code', u'url': u'/blogs/3/'},
        {u'stored_title': u'web testing python', u'url': u'/blogs/2/'},
    ]


Objects can be added or removed at any time from the index::

    >>> site.store_object(some_blog_instance)
    >>> site.remove_object(some_other_obj)


If you have multiple types of objects in your autocomplete index, you can restrict
results to a certian type by passing in "models" to the suggest method::

    >>> site.suggest('python', models=[Blog, Photo])


Configuring
-----------

The `AUTOCOMPLETE_BACKEND` setting allows you to specify which backend to use for autocomplete.  The options are:

* completion.backends.db_backend.DatabaseAutocomplete
* completion.backends.redis_backend.RedisAutocomplete
* completion.backends.solr_backend.SolrAutocomplete


Configuring Redis
^^^^^^^^^^^^^^^^^

Make sure that you have `Redis <http://github.com/antirez/redis/>`_ and `redis-py <http://github.com/andymccurdy/redis-py/>`_ installed.

Add something like the following to your settings file, where the connection string is <host name>:<port>:<database> ::

    AUTOCOMPLETE_REDIS_CONNECTION = 'localhost:6379:0'


Configuring Solr
^^^^^^^^^^^^^^^^

Make sure that you have `Solr <http://lucene.apache.org/solr/>`_ and `pysolr <http://github.com/toastdriven/pysolr/>`_ installed.

Add something like this to your settings file::

    AUTOCOMPLETE_SOLR_CONNECTION = 'http://localhost:8080/solr/autocomplete-core/'

Additionally, if you end up using Solr (which I'd recommend!), you will need to ensure you have the correct field definitions in your solr schema.  A sample schema can be generated for you automatically, by running::

    django-admin.py autocomplete_schema

This will drop a file named ``schema.xml`` in your current directory.


Installation
------------

`python setup.py install`

OR

put the ``completion`` folder on your python-path
