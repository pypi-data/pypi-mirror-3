#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import defaultdict
import re
import sys
import logging

from base_command import BaseCommand
from helpers import true_categories

log = logging.getLogger("greader2org")

CHANGES_LIMIT = 10000

class UpdateToGoogle(BaseCommand):
    """
    Uzupełnia plik feeds.org na bazie zawartości w Google
    """

    def execute(self):

        rc = self.reader

        subs = rc.get_subscription_list()
        
        # tag (dla nieotagowanych 'ZZZ: Unlabeled') ---> lista elementów
        subscribed = defaultdict(lambda : [])
        
        # Klucz: url feedu - ale BEZ postrankowych parametrów jeśli były.
        # Wartości: słowniczek o polach feed_url, title, categories (lista!)
        all_google_feeds = dict()
        
        re_par = re.compile("^(http://feeds.postrank.com.*)\?level=\w+$")
        
        for item in subs['subscriptions']:
            feed_url = item['id']
            if feed_url.startswith("feed/"):
                feed_url = feed_url[5:]
            elif feed_url.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed_url)
        
            title = item['title']
            cat = [ x['label'] for x in true_categories(item['categories']) ]
        
            key_url = feed_url
            m = re_par.match(key_url)
            if m:
                key_url = m.group(1)
        
            all_google_feeds[ key_url ] = dict(
                title = title, categories = cat, feed_url = feed_url )
        
        changes_count = 0
        
        for folder in self.org.folders:
            for feed in folder.feeds:
                gf = all_google_feeds.get( feed.feed )
                if not gf and feed.postrank_feed:
                    gf = all_google_feeds.get( feed.postrank_feed )
                if gf:
                    old_url = gf['feed_url']
        
                if 'disabled' in feed.tags:
                    if gf:
                        print "Disabled feed, unsubscribing: %s" % feed.title
                        rc.unsubscribe_feed(old_url)
                        changes_count += 1
                        if changes_count >= CHANGES_LIMIT:
                            sys.exit(0)
                    continue
        
                new_url = feed.feed
                if not ('private' in feed.tags) and feed.postrank_feed and feed.level:
                    if old_url and old_url.startswith(feed.postrank_feed):
                        print "Postrank is closed, no level-based filtering is possible. Resubscribing %s to default url" % feed.title
                    else:
                        print "Postrank is closed, no level-based filtering is possible, ignoring level tags in %s" % feed.title
                    #new_url = feed.postrank_feed
                    #if feed.level and feed.level in ['best', 'great', 'good']:
                    #    new_url += "?level=%s" % feed.level
        
                if not gf:
                    print "New (or un-disabled) feed, subscribing: %s" % feed.title
                    rc.subscribe_feed(new_url, feed.title)
                    rc.add_feed_tag(new_url, feed.title, folder.folder_label)
                    changes_count += 1
                    if changes_count >= CHANGES_LIMIT: sys.exit(0)
        
                elif new_url != old_url:
                    print "Feed url changed from %s to %s, resubscribing" % (old_url, new_url)
                    rc.subscribe_feed(new_url, feed.title)
                    rc.add_feed_tag(new_url, feed.title, folder.folder_label)
                    rc.unsubscribe_feed(old_url)
                    changes_count += 1
                    if changes_count >= CHANGES_LIMIT: sys.exit(0)
        
                else:
                    if feed.title != gf['title']:
                        print "Changing title from %s to %s" % (gf['title'], feed.title)
                        rc.change_feed_title(new_url, feed.title)
                    categories = gf['categories']
                    if not (folder.folder_label in categories):
                        print "Adding feed %s to folder %s" % (
                            feed.title, folder.folder_label)
                        rc.add_feed_tag(new_url, feed.title, folder.folder_label)
                        changes_count += 1
                        if changes_count >=CHANGES_LIMIT: sys.exit(0)
                    for cat in categories:
                        if cat != folder.folder_label:
                            print "Removing feed %s from folder %s" % (
                                feed.title, cat)
                            rc.remove_feed_tag(new_url, feed.title, cat)
                            changes_count += 1
                            if changes_count >= CHANGES_LIMIT: sys.exit(0)
        
                
