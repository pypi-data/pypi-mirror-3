#!/usr/bin/python
# -*- coding: utf-8 -*-

from mekk.feeds.orgfile import Folder, Feed
from collections import defaultdict
from base_command import BaseCommand
from helpers import true_categories
import logging, re

log = logging.getLogger("greader2org")

WARN_MULTIPLE_CATEGORIES = False

class UpdateFromGoogle(BaseCommand):
    """
    Uzupełnia plik feeds.org na bazie zawartości w Google
    """

    def execute(self):
        if not self.org.exists():
            raise Exception("%s does not exist. Use\n  greader2org init\nto create initial version" % self.org.file_name)

        subs = self.reader.get_subscription_list()

        # tag (dla nieotagowanych 'ZZZ: Unlabeled') ---> lista elementów
        subscribed = defaultdict(lambda : [])
        
        all_google_feeds = set()

        re_postrank = re.compile(
            r'^(http://feeds.postrank.com/[^\?]+)\?level=\w+$')
        
        for item in subs['subscriptions']:
            feed_url = item['id']
            if feed_url.startswith("feed/"):
                feed_url = feed_url[5:]
            elif feed_url.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed_url)
        
            # Czyszczenie postrankowatych
            m = re_postrank.match(feed_url)
            if m:
                feed_url = m.group(1)

            title = item['title']
        
            folder = "ZZZ: Unlabeled"
            cat = true_categories( item['categories'] )
            if len(cat) > 0:
                folder = cat[0]['label']
                if len(cat) > 1:
                    if WARN_MULTIPLE_CATEGORIES:
                        log.warn("Multiple categories for %s. Using first one of: %s" % (
                            item['id'], ", ".join((x['label'] for x in cat))))
        
            if not self.org.find_feed(feed_url):
                print "New feed %s in category %s" % (title, folder)
                lab = self.org.find_or_create_folder(folder)
                lab.add_feed(
                    Feed(title, [], feed_url, None, None, None) )
        
            all_google_feeds.add(feed_url)
        
        # Disabledy
        
        for folder in self.org.folders:
            for feed in folder.feeds:
                if feed.feed in all_google_feeds:
                    continue
                if feed.postrank_feed and (feed.postrank_feed in all_google_feeds):
                    continue
                if not 'disabled' in feed.tags:
                    print "Marking unsubscribed feed %s as disabled" % feed.title
                    feed.tags.append('disabled')
        
        self.org.save_to()
