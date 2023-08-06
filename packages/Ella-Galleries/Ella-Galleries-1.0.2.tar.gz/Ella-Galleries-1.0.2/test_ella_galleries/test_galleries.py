# -*- coding: utf-8 -*-
from datetime import datetime
from django.test import TestCase
from django.test.utils import setup_test_environment

from nose import tools

from test_ella.test_core import create_basic_categories
from test_ella.test_photos.fixtures import create_photo
from test_ella import template_loader

# FIXME hack alert - we are calling the registration here, it should be dealt
# with in the project itself somehow
from ella_galleries import register
from ella_galleries.models import Gallery

def create_and_publish_gallery(case):
    case.publishable = Gallery.objects.create(
        title=u'First Gallery',
        slug=u'first-gallery',
        description=u'Some\nlonger\ntext',
        category=case.category_nested,
        content=u'Some\neven\nlonger\ntext',
        publish_from=datetime(2008, 1, 10),
        published=True
    )

    case.p1 = create_photo(case)
    case.p2 = create_photo(case, slug='another-photo')

    case.galitem = case.publishable.galleryitem_set.create(
        photo=case.p1,
        order=0
    )

    case.galitem2 = case.publishable.galleryitem_set.create(
        photo=case.p2,
        order=1
    )

    case.galitem3 = case.publishable.galleryitem_set.create(
        photo=case.p1,
        order=2
    )

class TestGalleries(TestCase):

    def setUp(self):
        super(TestGalleries, self).setUp()
        create_basic_categories(self)
        create_and_publish_gallery(self)
        template_loader.templates['page/item.html'] = 'page/item.html'

    def tearDown(self):
        super(TestGalleries, self).tearDown()
        template_loader.templates = {}

    def test_get_photo_returns_first_items_photo(self):
        tools.assert_equals(self.p1, self.publishable.get_photo())

    def test_gallery_url(self):
        tools.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/', self.publishable.get_absolute_url())

    def test_gallery_custom_url_first_item(self):
        tools.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/', self.galitem.get_absolute_url())

    def test_gallery_custom_url_item(self):
        tools.assert_equals('/nested-category/2008/1/10/galleries/first-gallery/item/%s/' % self.p2.slug, self.galitem2.get_absolute_url())

    def test_gallery_custom_view_first_item(self):
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/')

        tools.assert_true('previous' in response.context)
        tools.assert_equals(None, response.context['previous'])

        tools.assert_true('next' in response.context)
        tools.assert_equals(self.galitem2, response.context['next'])

        tools.assert_true('item' in response.context)
        tools.assert_equals(self.galitem, response.context['item'])

        tools.assert_true('position' in response.context)
        tools.assert_equals(1, response.context['position'])

        tools.assert_true('count' in response.context)
        tools.assert_equals(3, response.context['count'])

    def test_gallery_custom_view_item_raises_404_on_non_existent_slug(self):
        template_loader.templates['404.html'] = ''
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/non-existent-slug/')
        tools.assert_equals(404, response.status_code)

    def test_gallery_custom_view_item(self):
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/item/%s/' % self.p2.slug)

        tools.assert_true('previous' in response.context)
        tools.assert_equals(self.galitem, response.context['previous'])

        tools.assert_true('next' in response.context)
        tools.assert_equals(self.galitem3, response.context['next'])

        tools.assert_true('item' in response.context)
        tools.assert_equals(self.galitem2, response.context['item'])

        tools.assert_true('position' in response.context)
        tools.assert_equals(2, response.context['position'])

        tools.assert_true('count' in response.context)
        tools.assert_equals(3, response.context['count'])

    def test_duplicit_photo_works_and_gets_updated_slug(self):
        tools.assert_equals(self.p1.slug + '1', self.galitem3.get_slug())
        response = self.client.get('/nested-category/2008/1/10/galleries/first-gallery/item/%s1/' % self.p1.slug)

        tools.assert_true('previous' in response.context)
        tools.assert_equals(self.galitem2, response.context['previous'])

        tools.assert_true('next' in response.context)
        tools.assert_equals(None, response.context['next'])

        tools.assert_true('item' in response.context)
        tools.assert_equals(self.galitem3, response.context['item'])

        tools.assert_true('position' in response.context)
        tools.assert_equals(3, response.context['position'])

        tools.assert_true('count' in response.context)
        tools.assert_equals(3, response.context['count'])



