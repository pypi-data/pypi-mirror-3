import random
import re

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase, Client, RequestFactory
from django.views.generic import View

from .api import API as api
from .models import Author, Book
from .resourses import AuthorResource, BookPrefixResource, ArticleResource, SomeOtherResource, BookResource
from adrest.mixin.emitter import EmitterMixin
from adrest.models import Access
from adrest.tests.utils import AdrestTestCase
from adrest.utils import serializer, paginator, emitter, parser


class MixinTest(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def test_emitter(self):
        request = self.rf.get("/")
        class Test(View, EmitterMixin):
            def get(self, request):
                content = self.emit('test')
                response = HttpResponse(content)
                return response
        test = Test()
        response = test.dispatch(request)
        self.assertContains(response, 'test')


class MetaTest(TestCase):

    def test_meta(self):
        self.assertTrue(AuthorResource.meta)
        self.assertEqual(AuthorResource.allowed_methods, (
            'GET', 'POST', 'OPTIONS', 'HEAD'
        ))
        self.assertEqual(AuthorResource.meta.name, 'author')
        self.assertEqual(AuthorResource.meta.url_name, 'author')
        self.assertEqual(AuthorResource.meta.url_regex, '^owner/$')
        self.assertEqual(AuthorResource.meta.parents, [])
        self.assertEqual(AuthorResource.meta.emitters_dict, {
            emitter.JSONEmitter.media_type: emitter.JSONEmitter,
        })
        self.assertEqual(AuthorResource.meta.emitters_types, [
            emitter.JSONEmitter.media_type,
        ])
        self.assertEqual(AuthorResource.meta.default_emitter, emitter.JSONEmitter)
        self.assertEqual(AuthorResource.meta.parsers_dict, {
            parser.FormParser.media_type: parser.FormParser,
            parser.XMLParser.media_type: parser.XMLParser,
            parser.JSONParser.media_type: parser.JSONParser,
        })
        self.assertEqual(AuthorResource.meta.default_parser, parser.FormParser)

    def test_meta_parents(self):
        self.assertEqual(AuthorResource.meta.parents, [])
        self.assertEqual(BookPrefixResource.meta.parents, [AuthorResource])
        self.assertEqual(ArticleResource.meta.parents, [AuthorResource, BookPrefixResource])

    def test_meta_name(self):
        self.assertEqual(AuthorResource.meta.name, 'author')
        self.assertEqual(BookPrefixResource.meta.name, 'book')
        self.assertEqual(SomeOtherResource.meta.name, 'someother')

    def test_meta_url_name(self):
        self.assertEqual(AuthorResource.meta.url_name, 'author')
        self.assertEqual(BookResource.meta.url_name, 'author-book')
        self.assertEqual(BookPrefixResource.meta.url_name, 'author-test-book')
        self.assertEqual(ArticleResource.meta.url_name, 'author-test-book-article')
        self.assertEqual(SomeOtherResource.meta.url_name, 'author-device-someother')

    def test_meta_url_regex(self):
        self.assertEqual(AuthorResource.meta.url_regex, '^owner/$')
        self.assertEqual(BookPrefixResource.meta.url_regex, 'owner/test/book/(?:(?P<book>[^/]+)/)?')
        self.assertEqual(ArticleResource.meta.url_regex, 'owner/book/(?P<book>[^/]+)/article/(?:(?P<article>[^/]+)/)?')
        self.assertEqual(SomeOtherResource.meta.url_regex, 'owner/device/(?P<device>[^/]+)/someother/(?:(?P<someother>[^/]+)/)?')


class ApiTest(AdrestTestCase):

    api = api

    def test_api(self):
        self.assertTrue(api.version)
        self.assertEqual(str(api), "1.0.0")
        self.assertTrue(api.urls)

    def test_urls(self):
        uri = self.reverse('test')
        self.assertEqual(uri, '/1.0.0/test/mem')


class AdrestTest(AdrestTestCase):

    api = api

    def setUp(self):
        user = User.objects.create(username='test')
        self.author = Author.objects.create(name='John', user=user)
        self.book = Book.objects.create(author=self.author, title='test', status=1)
        super(AdrestTest, self).setUp()

    def test_methods(self):
        uri = self.reverse('author')
        self.assertEqual(uri, '/1.0.0/owner')
        response = self.client.get(uri)
        self.assertContains(response, 'true')

        response = self.client.put(uri)
        self.assertContains(response, 'false', status_code=405)

        response = self.client.head(uri)
        self.assertEqual(response.status_code, 200)

    def test_owner(self):
        response = self.get_resource('author-test-book-article', book=self.book.pk, data=dict(
            author = self.author.pk
        ))
        self.assertContains(response, 'false', status_code=401)

        response = self.get_resource('author-test-book-article', key = self.author.user.accesskey_set.get(),
                book=self.book.pk, data=dict(
                    author = self.author.pk
                ))
        self.assertContains(response, 'true')

    def test_log(self):
        uri = self.reverse('author-test-book-article', book=self.book.pk)
        self.client.get(uri)
        access = Access.objects.get()
        self.assertEqual(access.uri, uri)
        self.assertEqual(access.version, str(api))

    def test_options(self):
        self.assertTrue('OPTIONS' in ArticleResource.allowed_methods)
        uri = self.reverse('author-test-book-article', book=self.book.pk)
        response = self.client.options(uri, data=dict(
            author = self.author.pk,
        ))
        self.assertContains(response, 'OK')


class ResourceTest(AdrestTestCase):

    api = api

    def setUp(self):
        super(ResourceTest, self).setUp()
        for i in range(5):
            user = User.objects.create(username='test%s' % i )
            self.author = Author.objects.create(name='author%s' % i, user=user)

        for i in range(148):
            Book.objects.create(author=self.author, title="book%s" % i, status = random.choice((1, 2, 3)))

    def test_author(self):
        response = self.get_resource('author')
        self.assertContains(response, 'count="5"')

        response = self.post_resource('author', data=dict(name = "new author", user=User.objects.create(username="new user").pk))
        self.assertContains(response, 'new author')

    def test_book(self):
        uri = self.reverse('author-test-book')
        self.assertEqual(uri, "/1.0.0/owner/test/book/")

        response = self.get_resource('author-test-book', data=dict(
            author = self.author.pk
        ))
        self.assertContains(response, 'count="%s"' % Book.objects.filter(author=self.author).count())
        self.assertContains(response, '<name>%s</name>' % self.author.name)

        response = self.post_resource('author-test-book', data=dict(
            title = "new book",
            status=2,
            author = self.author.pk))
        self.assertContains(response, '<price>0</price>')

        uri = self.reverse('author-test-book', book=1)
        uri = "%s?author=%s" % (uri, self.author.pk)
        response = self.client.put(uri, data=dict(
            price = 100
        ))
        self.assertContains(response, '<price>100</price>')

        response = self.client.delete(uri)
        self.assertContains(response, 'Book has been deleted.')

    def test_filter(self):
        uri = self.reverse('author-test-book')
        response = self.client.get(uri, data=dict(
            author = self.author.pk,
            title="book2"))
        self.assertContains(response, 'count="1"')

        response = self.client.get(uri, data=dict(
            author = self.author.pk,
            status=[1, 2, 3]))
        self.assertContains(response, 'count="%s"' % Book.objects.all().count())

        response = self.client.get(uri, data=dict(
            author = self.author.pk,
            status=[1, 3]))
        self.assertNotContains(response, '<status>2</status>')

        response = self.client.get(uri + "?title=book2&title=book3&author=%s" % self.author.pk)
        self.assertContains(response, 'count="2"')

    def test_custom(self):
        uri = self.reverse('book')
        response = self.client.get(uri)
        self.assertContains(response, 'count="%s"' % Book.objects.all().count())
        book = Book.objects.create(author=self.author, title="book", status=1)
        response = self.client.get(uri)
        self.assertContains(response, 'count="%s"' % Book.objects.all().count())

        uri = self.reverse('author-test-book-article', book=book.pk) + "?author=" + str(self.author.pk)
        response = self.client.delete(uri,
                HTTP_AUTHORIZATION=self.author.user.accesskey_set.get().key)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[-1].subject, '[Django] ADREST API Error (500): /1.0.0/owner/book/%s/article/' % Book.objects.all().count())

        self.assertContains(response, 'Some error', status_code=500)

        response = self.client.put(uri, HTTP_AUTHORIZATION=self.author.user.accesskey_set.get().key)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[-1].subject, '[Django] ADREST API Error (400): /1.0.0/owner/book/%s/article/' % Book.objects.all().count())
        self.assertContains(response, 'Assertion error', status_code=400)

    def test_some_other(self):
        response = self.get_resource('test')
        self.assertContains(response, '<someother>True</someother>')
        self.assertContains(response, '<method>GET</method>')


    def test_books(self):
        """Test response Link header

        Example: </1.0.0/author/5/test/book/?page=2>; rel="next"
        """
        link_re = re.compile(r'<(?P<link>[^>]+)>\; rel=\"(?P<rel>[^\"]+)\"')

        response = self.get_resource('author-test-book',
                data=dict(author = self.author.pk))
        self.assertTrue(response.has_header("Link"))
        self.assertEquals(response["Link"], '<%s?page=2&author=5>; rel="next"' % self.reverse('author-test-book'))
        # Get objects by links on Link header
        response = self.client.get(link_re.findall(response['Link'])[0][0])

        links = link_re.findall(response['Link'])

        self.assertEquals(links[0][0], '%s?page=3&author=5' % self.reverse('author-test-book'))
        self.assertEquals(links[0][1], 'next')

        self.assertEquals(links[1][0], '%s?author=5' % self.reverse('author-test-book'))
        self.assertEquals(links[1][1], 'previous')


class AdrestMapTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_methods(self):
        uri = reverse("main-%s-map" % str(api))
        self.assertEqual(uri, "/%s/map" % api)
        response = self.client.get(uri)
        self.assertContains(response, 'MAP')
        self.assertContains(response, 'nickname')

        response = self.client.get(uri, HTTP_ACCEPT="application/json")
        self.assertNotContains(response, 'MAP')
        self.assertContains(response, '"price", {"required": false')


class SerializerTest(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        for i in range(1, 100):
            user = User.objects.create(username='test%s' % i)
            self.author = Author.objects.create(name='John %s' % i, user=user)
            self.book = Book.objects.create(author=self.author, title='test %s' % i, status=random.choice((1, 2, 3)))

    def test_json(self):
        authors = Author.objects.all()
        test = serializer.json_dumps(authors)
        self.assertTrue("main.author" in test)
        request = self.rf.get("/")
        pg = paginator.Paginator(request, authors, 10)
        test = serializer.json_dumps(pg)
        self.assertTrue("count" in test)
        books = Book.objects.all()
        test = serializer.json_dumps(books)
        self.assertTrue("author" in test)
        self.assertFalse("publisher" in test)

    def test_xml(self):
        authors = Author.objects.all()
        test = serializer.xml_dumps(authors)
        self.assertTrue("author" in test)
