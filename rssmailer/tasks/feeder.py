import hashlib
import logging
from datetime import datetime
from itertools import ifilter

from celery.decorators import task
from celery.decorators import periodic_task
from celery.execute import send_task
from django.conf import settings

import feedparser

from ..models import Channel, EntryHash
from mail import send

# RSS spec: http://cyber.law.harvard.edu/rss/rss.html

logger = logging.getLogger(__name__)

@task(ignore_result=True, name="rssmailer.tasks.feeder.update_feeds")
def update_feeds():
    channels = Channel.objects.all()
    for chan in channels:
        check_feed(chan)

def check_feed(channel):
    """Checks whether the given feed (channel) has new entries."""
    
    modified_header = None
    if channel.modified:
        modified_header = channel.modified.timetuple()
    
    feed = feedparser.parse(
        channel.url, etag=channel.etag, modified=modified_header)
    
    if feed.status == 200 and feed.has_key("entries"):
        # feed updated (or the server does not supports headers If-Modified etc. 
        new_entries = matcher(feed.entries)
        if not new_entries:
            logger.info("No new entries on %s" % feed.url)
            return
        
        logger.info("[%s] has %d new entries" % (feed.url, len(new_entries)))
        
        for entry in map(lambda e: e[1], new_entries):
            consumer = getattr(settings, "RSSMAILER_CONSUMER", "rssmailer.tasks.mail.send")
            send_task(consumer, args=[entry,])
        
        channel.etag = feed.get('etag', None)
        m = feed.get('modified', None)
        if m:
            channel.modified = datetime(*m[:6])
        channel.save()
        
        # update seen items
        for hash in map(lambda e: e[0], new_entries):
            e = EntryHash(hash)
            e.save()

        
    elif feed.status == 304: # not modified
        logger.info("Feed [%s] Not-modified" % feed.url)
    else: # some error code or redirection
        logger.warning("Unexpected error, status: %d" % feed.status)

    
def matcher(entries):
    """
    Matches hashes of the entries against seen hashes stored in database and
    returns list of new entries (whose hashes were not found in database).
    """
    current_entries_hash = map(hasher, entries)
    
    seen_hashes = EntryHash.objects.filter(hash__in=current_entries_hash)
    seen_hashes = map(lambda e: e.hash, seen_hashes)
    
    current_entries = zip(current_entries_hash, entries)
    new_entries = ifilter(lambda e: e[0] not in seen_hashes, current_entries)
    
    return list(new_entries)
    

def hasher(entry):
    """
    Returns hash representing the given entry.
    
    >>> entry = {"title": "foo", "description": "bar"}
    >>> hasher(entry)
    '3858f62230ac3c915f300c664312c63f'
    """

    criteria = getattr(settings, "RSSMAILER_UNIQUENESS",
                       ['title', 'description', 'guid', 'updated'])
    
    # Filter out criteria that cannot be used because they're missing
    criteria = ifilter(lambda c: entry.has_key(c), criteria)
    
    hash = ""
    for cr in criteria:
        hash += entry[cr]
    
    return hashlib.md5(hash.encode('utf-8')).hexdigest()
    