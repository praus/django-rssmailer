from celery.decorators import task
from django.core.mail import send_mail

from ..models import Email

@task(ignore_result=True, name="rssmailer.tasks.mail.send")
def send(entry, **kwargs):
    logger = send.get_logger(**kwargs)
    logger.info("Sending entry: %s" % entry.title)
    
    emails_all = Email.objects.all()
    step = 3  # how many recipients in one e-mail
    
    for i in range(0, len(emails_all), step):
        recipients = map(lambda e: e.email, emails_all[i:i+step])
        send_entry_to.delay(entry.title, entry.summary, recipients)


@task(ignore_result=True, name="rssmailer.tasks.mail.send_entry_to")
def send_entry_to(title, body, recipients, **kwargs):
    logger = send.get_logger(**kwargs)
    logger.info("Sending to: %s" % ','.join(recipients))
    send_mail(title, body, "rssmailer@praus.net", recipients)
