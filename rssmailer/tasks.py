from celery.decorators import task
from models import Email

@task
def send(entry, **kwargs):
    logger = send.get_logger(**kwargs)
    logger.info("Sending entry: %s" % entry.title)
    emails = Email.objects.all()
    for em in emails:
        send_entry_to.delay(entry.title, title.summary, em.email)

@task
def send_entry_to(title, content, email):
    logger = add.get_logger(**kwargs)
    logger.info("Sending to: %s" % email)