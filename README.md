RSS Mailer is a small django application for watching changes in channels
in pretty much any format supported by FeedParser library and sending these
changes by email.
It uses django-celery for asynchronous messaging.

Configuration (settings.py)
===========================

Celery setup
------------
    import djcelery
    djcelery.setup_loader()

Celery does not autodetect tasks package, we have to manually specify each task file
    CELERY_IMPORTS = (
        'rssmailer.tasks.feeder',
        'rssmailer.tasks.mail',
    )
    
For debugging purposes (rssmailer logs information about it's status mostly on INFO level):
    CELERYD_LOG_LEVEL = "INFO"

Broker setup (RabbitMQ)
-----------------------
This example uses RabbitMQ, but you can use anything that Celery supports.
    BROKER_HOST = "<server-address>"
    BROKER_PORT = <server-port>   *default 5672*
    BROKER_USER = "<username>"
    BROKER_PASSWORD = "<password>"
    BROKER_VHOST = "<vhost>"

Periodic feed updates
---------------------
update_feeds task should be regularly run. This example will run this task every
60 seconds. You can also use cron-like syntax, see Celery docs.

    from datetime import timedelta

    CELERYBEAT_SCHEDULE = {
        "update-feeds": {
            "task": "rssmailer.tasks.feeder.update_feeds",
            "schedule": timedelta(seconds=60),
        },
    }

rssmailer-specific settings
---------------------------
### Mandatory settings
    RSSMAILER_FROM = "<email-address-appearing-in-From-header>"
    
### Optional settings
How many recipients can be in one email. Problem is that we can possibly have
a lot of email address in our database and SMTP server might not be able to cope
with it if we sent them all in one email.

    RSSMAILER_RECIPIENTS = 3

Which attributes should be considered for computing uniqueness-hash of the entry?
RSS standard states that the only mandatory item in RSS <item> is <title> or <summary>.
Therefore we can't rely on ID.
    RSSMAILER_UNIQUENESS = ['title', 'description', 'guid', 'updated']
    
Which task should consume new entries? It has to be a Celery task (annotated, or inherited from Task) 
    RSSMAILER_CONSUMER = "rssmailer.tasks.mail.send"
    

TODO
====
- use Bcc while sending one email to multiple recipients
- consider using just guid for entry identification while it exists

