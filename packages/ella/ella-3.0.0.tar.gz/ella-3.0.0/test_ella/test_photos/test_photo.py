# -*- coding: utf-8 -*-
import os

from django.core.files.base import ContentFile
from django.test import TestCase
from django.contrib.sites.models import Site

from nose import tools

from ella.photos.models import Format, FormatedPhoto, redis, REDIS_FORMATTED_PHOTO_KEY

from test_ella.test_photos.fixtures import create_photo_formats, create_photo

class TestPhoto(TestCase):

    def setUp(self):
        super(TestPhoto, self).setUp()

        # fixtures
        create_photo_formats(self)

        create_photo(self)

    def test_formatted_photo_has_zero_crop_box_if_smaller_than_format(self):
        format = Format.objects.create(
            name='sample',
            max_width=300,
            max_height=300,
            flexible_height=False,
            stretch=False,
            nocrop=False
        )
        format.sites.add(Site.objects.get_current())

        fp = FormatedPhoto(photo=self.photo, format=format)
        fp.generate(False)
        tools.assert_equals((0,0,0,0), (fp.crop_left, fp.crop_top, fp.crop_width, fp.crop_height))



    def test_retrieving_formatted_photos_on_fly(self):
        formatted = FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_true('url' in formatted)
        if redis:
            expected = {
                'height': '20',
                'width': '20',
                'url': '/static/photos/2012/02/14/1-1-example-photo_12.jpg',
            }
            actual = redis.hgetall(REDIS_FORMATTED_PHOTO_KEY % (self.photo.id, self.basic_format.id))
            tools.assert_equals(expected.keys(), actual.keys())
            tools.assert_equals(expected['width'], actual['width'])
            tools.assert_equals(expected['height'], actual['height'])

    def test_formattedphoto_cleared_when_image_changed(self):
        FormatedPhoto.objects.get_photo_in_format(self.photo, self.basic_format)
        tools.assert_equals(1, len(self.photo.formatedphoto_set.all()))

        # let us create image again
        f = open(self.image_file_name)
        file = ContentFile(f.read())
        f.close()

        self.photo.image.save("newzaaah", file)
        self.photo.save()

        tools.assert_equals(0, len(self.photo.formatedphoto_set.all()))

    def test_retrieving_ratio(self):
        tools.assert_equals(2, self.photo.ratio())

    def tearDown(self):
        os.remove(self.image_file_name)
        if self.photo.pk:
            self.photo.delete()
        super(TestPhoto, self).tearDown()
        if redis:
            redis.flushdb()
