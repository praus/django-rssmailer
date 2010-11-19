from django.db import models

class EntryHash(models.Model):
    '''Model for storing hashes of seen entries.'''
    hash = models.CharField(max_length=255, primary_key=True)

class Channel(models.Model):
    '''Model for channels to crawl.'''
    url = models.URLField(max_length=255)
    modified = models.DateTimeField(null=True, editable=False)
    etag = models.CharField(max_length=255, null=True, editable=False)
    
    def __unicode__(self):
        return self.url

class Email(models.Model):
    '''Database models representing destination email addresses.'''
    email = models.EmailField()
    
    def __unicode__(self):
        return self.email
