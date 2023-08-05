# -*- coding: utf-8 -*-

from base_command import BaseCommand
from collections import defaultdict
from helpers import true_categories
from mekk.feeds.orgfile import Folder, Feed

import logging

log = logging.getLogger("greader2org")

class InitialLoad(BaseCommand):
    """
    Pierwszy import z Google Readera (stworzenie inicjalnej wersji
    pliku do zarządzania feedami)
    """

    def execute(self):

        if self.org.exists():
            raise Exception("File %s already exists.\nTo update it, use 'get' option instead of 'init'" % self.org.file_name)
        
        subs = self.reader.get_subscription_list()
        
        # tag (dla nieotagowanych 'ZZZ: Unlabeled') ---> lista elementów
        subscribed = defaultdict(lambda : [])
        
        for item in subs['subscriptions']:
            feed = item['id']
            if feed.startswith("feed/"):
                feed = feed[5:]
            elif feed.startswith("user/"):
                continue   # starred, broadcast itp
            else:
                raise Exception("Ugly feed: %s" % feed)
        
            title = item['title']
        
            label = "ZZZ: Unlabeled"
            cat = true_categories( item['categories'] )
            if len(cat) > 0:
                label = cat[0]['label']
                if len(cat) > 1:
                    log.warn("Multiple folders for %s. Using first one of: %s" % (
                        item['id'], ", ".join((x['label'] for x in cat))))
        
            subscribed[label].append( dict(feed = feed, title = title) )

        #org_save = file(self.org.org_file, "w")
        
        for label in sorted(subscribed.keys()):
            folder = Folder(label)
            self.org.add_folder(folder)

            print "Creating folder %s" % label

            #org_save.write("* %s\n\n" % label.encode("utf-8"))
            for info in subscribed[label]:
                #org_save.write( ("** %s\n\n   feed: %s\n\n" % (info['title'], info['feed'])).encode("utf-8") )
                feed = Feed(info['title'], [], info['feed'],
                            None, None, "")
                folder.add_feed(feed)
                print "   adding feed %s" % info['title']
        
        #org_save.close()
        self.org.save_to()
                
