import os
from unittest import skipIf
from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from django.core.files import File
from mock import patch
from ccstraps.models import Strap, StrapImage
from ccstraps.templatetags import ccstrap_tags

# we need mock for these tests
try:
    import mock
    skip_templatetagtestcases = False
except ImportError:
    skip_templatetagtestcases = True
# we need the test files
red = os.path.exists('%s/ccstraps/red.png' % settings.STATIC_ROOT)
purple = os.path.exists('%s/ccstraps/purple.png' % settings.STATIC_ROOT)

# the mock context
class ContextMock(dict):
    autoescape = object()


@skipIf(skip_templatetagtestcases, 'mock library required')
class TemplatetagTestCases(TestCase):

    @patch('django.template.loader.get_template')
    @patch('django.template.Context')
    def test_get_strap_none(self, get_template, Context):
        """get strap behaves as expected if no strap exists"""
        # get the node
        node = ccstrap_tags.StrapNode('test', 'strap')
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual(None, context['strap'])

    @patch('django.template.loader.get_template')
    @patch('django.template.Context')
    def test_get_strap_expected(self, get_template, Context):
        # make the straps
        s = Strap()
        s.name = 'test'
        s.save()
        # now create the strap image
        r = open('%s/ccstraps/red.png' % settings.STATIC_ROOT)
        s1  = StrapImage()
        s1.src = File(r, 'ccstraps/red.png')
        s1.order = Decimal('10.00')
        s1.strap = s
        s1.save()
        # Another
        p = open('%s/ccstraps/purple.png' % settings.STATIC_ROOT)
        s2  = StrapImage()
        s2.src = File(r, 'ccstraps/purple.png')
        s2.order = Decimal('1.00')
        s2.strap = s
        s2.save()
        # close the images
        r.close()
        p.close()
        # get the node
        node = ccstrap_tags.StrapNode('test', 'strap')
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual('test', context['strap'].name)

    def test_strap_js(self):
        """strap js returns a dict containing STATIC_URL"""
        self.assertEqual(
                settings.STATIC_URL,
                ccstrap_tags.strap_js()['STATIC_URL'])

    def test_strap_css(self):
        """strap css returns a dict containing STATIC_URL"""
        self.assertEqual(
                settings.STATIC_URL,
                ccstrap_tags.strap_css()['STATIC_URL'])


