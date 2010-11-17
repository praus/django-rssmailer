from datetime import datetime
from itertools import takewhile, ifilter
import hashlib
import pdb
from celery.decorators import task
from celery.decorators import periodic_task
import feedparser

from ..models import Channel
from mail import send

# RSS spec: http://cyber.law.harvard.edu/rss/rss.html

@task(ignore_result=True, name="rssmailer.tasks.feeder.update_feeds")
def update_feeds():
    channels = Channel.objects.all()
    for chan in channels:
        check_feed(chan)

def check_feed(channel):
    """Checks whether the given feed has new entries."""
    
    modified_header = None
    if channel.modified:
        modified_header = channel.modified.timetuple()
    
    feed = feedparser.parse(
        channel.url, etag=channel.etag, modified=modified_header)
    
    if feed.status == 200: # feed updated
        new_entries = matcher(channel.last_item_seen, feed.entries)
        
        if not new_entries:
            print "No new entries on %s" % feed.url
            return
        
        for entry in new_entries:
            send.delay(entry)
        
        channel.etag = feed.get('etag', None)
        
        m = feed.get('modified', None)
        if m:
            channel.modified = datetime(*m[:6])
            
        channel.save()
        
        # update last item seen
        try:
            channel.last_item_seen = hasher(feed.entries[0])
            channel.save()
        except IndexError:
            print "Feed does not have any items!"
        
    elif feed.status == 304: # not modified
        print "Not modified"
    else: # some error code or redirection
        print "Error"

    
def matcher(last_item_seen, entries):
    """
    This function attempts to identify last item seen in the feed and
    subsequently returns newer items (in terms of order of appearance,not date!).
    """    
    return list(takewhile(lambda x: hasher(x) != last_item_seen, entries))
    

def hasher(entry):
    """Returns hash representing the given entry."""
    # TODO: make criteria configurable
    criteria = ['title', 'description', 'guid', 'updated']
    
    # Filter out criteria that cannot be used because they're missing
    criteria = ifilter(lambda c: entry.has_key(c), criteria)
    
    hash = ""
    for cr in criteria:
        hash += entry[cr]
    
    return hashlib.md5(hash.encode('utf-8')).hexdigest()
    