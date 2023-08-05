from django.test import TestCase
from feeds import XXXMODEL_NAMEXXXFeed
from models import XXXMODEL_NAMEXXX
from random_instances import get_or_create_random
from xml.etree.ElementTree import XML


class FeedTestCase(TestCase):
    '''Test suite for the Blog Feed.'''
    urls = 'XXXFOLDERXXX.urls'
    
    def _get_feed(self):
        return XML(self.client.get('/feed/').content).find('./channel')
    
    def test_feed_title(self):
        feed = self._get_feed()
        title = feed.find('./title').text
        self.assertEqual(title, XXXMODEL_NAMEXXXFeed.title)
        
    def test_feed_description(self):
        feed = self._get_feed()
        description = feed.find('./description').text
        self.assertEqual(description, XXXMODEL_NAMEXXXFeed.description)
        
    def test_feed_without_items(self):
        XXXMODEL_NAMEXXX.objects.all().delete()
        feed = self._get_feed()
        any_item = feed.find('./item')
        self.assertIsNone(any_item)
    
    def _match_XXXVAR_NAMEXXX(self, XXXVAR_NAMEXXX, item):
        return all([getattr(XXXVAR_NAMEXXX, attr.tag, attr.text) == attr.text 
            for attr in item._children])

    def test_feed_with_items(self):
        XXXVAR_NAMEXXX = get_or_create_random(XXXMODEL_NAMEXXX)
        feed = self._get_feed()
        items = feed.findall('./item')
        self.assertTrue(any([self._match_XXXVAR_NAMEXXX(XXXVAR_NAMEXXX, item)
            for item in items]))
