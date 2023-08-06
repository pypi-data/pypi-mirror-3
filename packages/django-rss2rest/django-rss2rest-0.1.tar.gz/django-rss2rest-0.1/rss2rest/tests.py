import os
from django.test import TestCase

from parser import FeedParser
from models import FeedItem

location = os.path.join(os.path.dirname(os.path.realpath(__file__)))

class FeedParserTestCase(TestCase):

    def setUp(self):
        item = FeedItem.objects.create(source_title='Test video',
            source_description='About test video',
            source_id='test-id-123',
            source_url='http://vimeo.com/test-vid',
            source_pub_date='2012-06-05 17:42:40'
        )
        self.parser = FeedParser(location + '/samples/vimeo-likes.rss', 'rss2rest.FeedItem')

    def test_count(self):
        entry_count = self.parser.count()
        self.assertEquals(25, entry_count)

    def test_convert_to_entry_list(self):
        list = self.parser.sync_feed_items()
        self.assertEquals(25, len(list))

    def test_does_video_exist(self):
        self.assertTrue(self.parser._does_item_exist('test-id-123'))
        self.assertFalse(self.parser._does_item_exist('test-id-999'))

    def test_create_video_from_entry_dict(self):
        entry = {
            "author":"Lorem",
            "author_detail": {"name":"Lorem"},
            "authors": [{}],
            "guidislink":False,
            "href":"",
            "id":"tag:vimeo,2012-04-28:clip36399067",
            "link":"http://vimeo.com/36399067",
            "links":[
                {"href":"http://vimeo.com/36399067",
                "rel":"alternate",
                "type":"text/html"},
                {"href":"http://vimeo.com/moogaloop.swf?clip_id=36399067",
                "length":"26666031",
                "rel":"enclosure",
                "type":"application/x-shockwave-flash"}],
            "media_content": [{}],
            "media_credit":{
                "role":"author",
                "scheme":"http://vimeo.com/clementandco"},
            "media_player":{
                "content":"",
                "url":"http://vimeo.com/moogaloop.swf?clip_id=36399067"},
            "media_thumbnail":[
                {"height":"150",
                "url":"http://b.vimeocdn.com/ts/249/652/249652963_200.jpg",
                "width":"200"}],
            "published":"Sat, 28 Apr 2012 17:32:36 -0400",
            "published_parsed":"2012-04-28 21:32:36",
            "summary":"Lorem ipsum dolor sit amet",
            "summary_detail":{
                "base":"http://vimeo.com/gumptv/likes/rss",
                "language":None,
                "type":"text/html",
                "value":"Lorem ipsum"},
            "title":"Lorem ipsum",
            "title_detail":{
                "base":"http://vimeo.com/gumptv/likes/rss",
                "language":None,
                "type":"text/plain",
                "value":"Lorem ipsum"}
        }

        item = self.parser._create_item_from_entry_dict(entry)
        self.assertEquals('Lorem ipsum', item.source_title)
        self.assertEquals('Lorem ipsum dolor sit amet', item.source_description)
        self.assertEquals('tag:vimeo,2012-04-28:clip36399067', item.source_id)
        self.assertEquals('http://vimeo.com/36399067', item.source_url)
        self.assertEquals('http://vimeo.com/36399067', item.source_url)

