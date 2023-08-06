import uuid
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

from invitable.hooks import connect_hooks

def token_gen():
    while True:
        token = str(uuid.uuid4()).replace('-', '')
        if not Invitation.objects.filter(token=token).count():
            break
    return token


INVITABLE_USER = getattr(settings, "INVITABLE_USER", User)
INVITABLE_HTML_EMAIL = getattr(settings, "INVITABLE_HTML_EMAIL", False)
INVITABLE_EMAIL_FROM = getattr(settings, "INVITABLE_EMAIL_FROM", "no-reply@example.com")
INVITABLE_TOKEN_GEN = getattr(settings, "INVITABLE_TOKEN_GEN", token_gen)
INVITABLE_TOKEN_LENGTH = getattr(settings, "INVITABLE_TOKEN_LENGTH", 64)


class Invitation(models.Model):
    user = models.ForeignKey(INVITABLE_USER)
    token = models.CharField(max_length=INVITABLE_TOKEN_LENGTH)
    email = models.EmailField(unique=True, db_index=True)
    account_type = models.CharField(max_length=64, null=True, blank=True)

    sent_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "Validation for [%s]" % (self.email)

    def before_create(self):
        self.token = INVITABLE_TOKEN_GEN()

    def after_create(self):
        # Send invitation on email

        # invitable/invitation_subject.txt
        # invitable/invitation.txt
        # invitable/invitation.html
        current_site = Site.objects.get_current()
        context = Context({'user': self.user,
                           'email': self.email,
                           'token': self.token,
                           'site': current_site})

        subject = loader.get_template("invitable/invitation_subject.txt").render(context)
        text_body = loader.get_template("invitable/invitation_body.txt").render(context)

        email = EmailMultiAlternatives(subject.rstrip('\n'), text_body,
                                       INVITABLE_EMAIL_FROM, [self.email])

        if INVITABLE_HTML_EMAIL:
            html_body = loader.get_template("invitable/invitation_body.html").render(context)
            email.attach_alternative(html_body, "text/html")

        email.send()

        self.send_at = datetime.datetime.now()
        self.save()

connect_hooks(Invitation)
