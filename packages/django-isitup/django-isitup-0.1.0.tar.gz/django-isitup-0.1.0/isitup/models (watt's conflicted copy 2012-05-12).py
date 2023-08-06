import time
import logging
import threading
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timesince import timesince

from django.template.loader import render_to_string
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from cache_utils.decorators import cached
from django.core.mail import send_mail
from django.contrib.sites.models import Site

from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel

from isitup import signals as custom_signals
from isitup import utils as custom_utils

bnull = { 'blank':True, 'null':True }

SUCCESS_CODES=getattr(settings, 'ISITUP_SUCCESS_CODES', [200,301,304])
STATUS_INTERVAL=getattr(settings, 'ISITUP_STATUS_INTERVAL', timedelta(minutes=5))

class ServiceOutage(TimeStampedModel):
    service = models.ForeignKey('Service')
    start = models.DateTimeField(_('Outage start'), default=datetime.now())
    end = models.DateTimeField(_('Outage end'), **bnull)
    response_code=models.CharField(_('Response code'), max_length=4, **bnull)

    class Meta:
        get_latest_by='created'

    def __unicode__(self):
        return 'Service check for %s on %s' % (self.service, self.created)

    @property
    def duration(self):
        return timesince(self.start, self.end)

    @property
    def resolved(self):
        if self.end < datetime.now():
            return True
        else:
            return False

class ServiceCheck(TimeStampedModel):
    service = models.ForeignKey('Service')
    status_code=models.CharField(_('Status code'), max_length=4, **bnull)
    response_time=models.FloatField(_('Response time'), **bnull)

    class Meta:
        get_latest_by='created'

    def __unicode__(self):
        return 'Service check for %s on %s' % (self.service, self.created)

class Service(TitleSlugDescriptionModel, TimeStampedModel):
    host=models.CharField(_('Host'), max_length=255)
    path=models.CharField(_('Path'), max_length=255, **bnull)
    frequency=models.CharField(_('Frequency'), max_length=20, default='*/5 * * * *')
    last_checked = models.DateTimeField(_('Last checked'), **bnull)
    owner=models.ForeignKey(User, blank=True)
    recipients=models.ManyToManyField(User, blank=True, related_name='recipients')
    active=models.BooleanField(_('Active'), default=False)

    def __unicode__(self):
        return self.title
            
    class Meta:
        verbose_name=_('Service')
        verbose_name_plural=_('Service')

    def _check_now(self):
        check = False
        if STATUS_INTERVAL == None:
            check = True
        elif self.ongoing_outages():
            check = True
        else:
            if self.active:
                if self.last_checked:
                    if self.last_checked + STATUS_INTERVAL < datetime.now():
                        check = True
                else:
                    check = True
        return check 

    def check_status_code(self):
        if self._check_now():
            if self.path:
                start = time.time()
                response = custom_utils.get_status_code(self.host, self.path)
                end = time.time()
            else:
                start = time.time()
                response= custom_utils.get_status_code(self.host)
                end = time.time()
            check=ServiceCheck.objects.create(service=self, status_code=response, response_time=end-start)
            check.save()
            self.last_checked = datetime.now()
            self.save()
        if self.status_code not in SUCCESS_CODES:
            if not self.ongoing_outages():
                outage = ServiceOutage.objects.create(service=self, start=datetime.now(), response_code=self.status_code)
                outage.save()
                custom_signals.response_error_received.send(sender=self, 
                                                             instance=self, 
                                                             host=self.host, 
                                                             user=self.owner,
                                                             template='isitup/response_error_email.txt',
                                                             recipients=self.recipients,
                                                             response_code=self.status_code)
        return self.status_code

    @property
    def history(self):
        return self.servicecheck_set.all()[:10]

    @property
    def up(self):
        self._up= False
        if self.status_code in SUCCESS_CODES: 
            self._up= True
        else: 
            self._up= False
        return self._up

    @property
    @cached(1200)
    def uptime_rate(self):
        checks = self.servicecheck_set.all()
        successes=0.0
        for check in self.servicecheck_set.all():
            if check.status_code:
                if int(check.status_code) in SUCCESS_CODES:
                     successes += 1.0
        return float(successes)/float(checks.count()) * 100

    @property
    @cached(1200)
    def uptime(self):
        latest_check = self.servicecheck_set.latest().created
        last_down_date=None
        for check in self.servicecheck_set.all():
            if check.status_code:
                if not int(check.status_code) in SUCCESS_CODES:
                    last_down_date = check.created
                    break
        if last_down_date:
            days = (latest_check - last_down_date).days
        else:
            days = (latest_check - self.servicecheck_set.all().reverse()[0].created).days 
        return days

    @property
    @cached(1200)
    def avg_response_time(self):
        ''' Average up all the response times where the respones code was OK'''
        total=0.0
        for check in self.servicecheck_set.all():
            if check.status_code:
                if int(check.status_code) in SUCCESS_CODES:
                    total += float(check.response_time)
        return float(total) / float(self.servicecheck_set.all().count())

    @property
    def status_code(self):
        try:
            code = int(self.servicecheck_set.latest().status_code)
        except:
            code = None
        return code

    def ongoing_outages(self):
        return self.serviceoutage_set.filter(end=None)

class ServiceNoticeEmailThread(threading.Thread):
    def __init__(self, instance, host, response_code, user, template, recipients):
        self.instance = instance
        self.host = host
        self.response_code = response_code
        self.user = user
        self.template = template
        self.recipients = recipients
        threading.Thread.__init__(self)

    def run(self):
        current_site = Site.objects.get_current()
        subject = "%s - %s responding with %s code" % ( current_site.name, self.host, self.response_code)
        message = render_to_string(
                self.template,
                { 'host': self.host,
                  'response_code': self.response_code,
                  'current_site': current_site })
        for recipient in self.recipients:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient.email])
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email])
        # The actual code we want to run, i.e. sending the email

    @receiver(custom_signals.response_error_received)
    def send_error_email(signal, instance, sender, host, response_code, user, template, recipients, *args, **kwargs):
        ServiceNoticeEmailThread(instance,host,response_code, user, template, recipients).start()

    @receiver(custom_signals.response_error_resolved)
    def send_resolve_email(signal, instance, sender, host, response_code, user, template, recipients, *args, **kwargs):
        ServiceNoticeEmailThread(instance,host,response_code, user,template, recipients).start()
