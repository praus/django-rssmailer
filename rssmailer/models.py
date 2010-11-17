from django.db import models

#class Item(models.Model):   
#    title = models.TextField(null=True)
#    description = models.TextField(null=True)
#    guid = models.CharField(max_length=255, null=True)
#    updated = models.DateTimeField(null=True)
#    
#    def __init__(self, title=None, desc=None, guid=None, updated=None):
#        self.title = title
#        self.description = desc
#        self.guid = guid
#        self.updated = updated
#    
#    def __unicode__(self):
#        return self.title

class Channel(models.Model):
    '''Model for channels to crawl.'''
    url = models.URLField(max_length=255)
    modified = models.DateTimeField(null=True, editable=False)
    etag = models.CharField(max_length=255, null=True, editable=False)
    last_item_seen = models.CharField(max_length=255, editable=False, null=True)
    
    def __unicode__(self):
        return self.url

class Email(models.Model):
    '''Database models representing destination email addresses.'''
    email = models.EmailField()
    
    def __unicode__(self):
        return self.email