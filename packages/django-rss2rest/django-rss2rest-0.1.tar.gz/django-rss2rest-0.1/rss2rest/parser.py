import string
import feedparser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import get_model


class FeedParser(object):

    def __init__(self, feed_source, model, mapping=None):
        app_name, model_name = model.split('.')
        self.model = get_model(app_name, model_name)
        self.valid_chars = "'-_.() %s%s" % (string.ascii_letters, string.digits)
        self.source = feed_source
        self.feed = feedparser.parse(self.source)

    def count(self):
        return len(self.feed.entries)

    def sync_feed_items(self):
        items = []

        for entry in self.feed.entries:
            if not self._does_item_exist(source_id=entry['id']):
                item = self._create_item_from_entry_dict(entry)
                item.save()
                items.append(item)
        return items

    def _does_item_exist(self, source_id):
        try:
            self.model.objects.get(source_id=source_id)
            return True
        except ObjectDoesNotExist:
            return False

    def _create_item_from_entry_dict(self, entry):
        item = self.model()

        for key in item.MAPPING.keys():
            value_key = item.MAPPING[key]
            item.__setattr__(key, entry[value_key])
        return item


class MultiFeedParser(object):

    def parse_feeds(self, feed_list):

        for feed in feed_list:
            parser = FeedParser(feed['url'], feed['model'])
            parser.sync_feed_items()

