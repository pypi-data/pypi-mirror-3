from __future__ import with_statement

from django.contrib.sites.models import Site

from django_hosts.middleware import HostsMiddleware
from django_hosts.tests.base import (override_settings, HostsTestCase,
                                     RequestFactory)
from django_hosts.tests.models import Author, BlogPost, WikiPage


class SitesTests(HostsTestCase):

    def setUp(self):
        super(SitesTests, self).setUp()
        self.site1 = Site.objects.create(domain='wiki.site1', name='site1')
        self.site2 = Site.objects.create(domain='wiki.site2', name='site2')
        self.site3 = Site.objects.create(domain='wiki.site3', name='site3')
        self.page1 = WikiPage.objects.create(content='page1', site=self.site1)
        self.page2 = WikiPage.objects.create(content='page2', site=self.site1)
        self.page3 = WikiPage.objects.create(content='page3', site=self.site2)
        self.page4 = WikiPage.objects.create(content='page4', site=self.site3)

        self.author1 = Author.objects.create(name='john', site=self.site1)
        self.author2 = Author.objects.create(name='terry', site=self.site2)
        self.post1 = BlogPost.objects.create(content='post1',
                                             author=self.author1)
        self.post2 = BlogPost.objects.create(content='post2',
                                             author=self.author2)

    def tearDown(self):
        for model in [WikiPage, BlogPost, Author, Site]:
            model.objects.all().delete()

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_sites_callback(self):
        rf = RequestFactory(HTTP_HOST='wiki.site1')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.simple')
        self.assertEqual(request.site, self.site1)

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_sites_callback_with_parent_host(self):
        rf = RequestFactory(HTTP_HOST='wiki.site2')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.simple')
        self.assertEqual(request.site, self.site2)

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_manager_simple(self):
        rf = RequestFactory(HTTP_HOST='wiki.site2')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.simple')
        self.assertEqual(request.site, self.site2)
        self.assertEqual(list(WikiPage.on_site.by_request(request)),
                         [self.page3])

    @override_settings(
        ROOT_HOSTCONF='django_hosts.tests.hosts.simple',
        DEFAULT_HOST='www')
    def test_manager_missing_site(self):
        rf = RequestFactory(HTTP_HOST='static')
        request = rf.get('/simple/')
        middleware = HostsMiddleware()
        middleware.process_request(request)
        self.assertEqual(request.urlconf, 'django_hosts.tests.urls.simple')
        self.assertRaises(AttributeError, lambda: request.site)
        self.assertEqual(list(WikiPage.on_site.by_request(request)), [])

    def test_manager_default_site(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertEqual(list(WikiPage.on_site.all()),
                             [self.page1, self.page2])

    def test_manager_related_site(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertEqual(list(BlogPost.on_site.all()), [self.post1])
        with self.settings(SITE_ID=self.site2.id):
            self.assertEqual(list(BlogPost.on_site.all()), [self.post2])

    def test_no_select_related(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertEqual(list(BlogPost.no_select_related.all()),
                             [self.post1])

    def test_non_existing_field(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertRaises(ValueError, BlogPost.non_existing.all)

    def test_dead_end_field(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertRaises(ValueError, BlogPost.dead_end.all)

    def test_non_rel_field(self):
        with self.settings(SITE_ID=self.site1.id):
            self.assertRaises(TypeError, BlogPost.non_rel.all)
