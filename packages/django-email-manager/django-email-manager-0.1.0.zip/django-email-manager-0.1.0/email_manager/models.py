# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings


class EmailLog(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=100, null=True, blank=True) # max_length=100 to store just the beginning of the subject
    date = models.DateField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s: %s' % (self.email, self.subject)

    @staticmethod
    def create_log(email, subject, success=True, error=None):
        if error:
            if success:
                error = None # to avoid inconsistent data caused by bad use of this method
            else:
                error = error[0:255]
        return EmailLog.objects.create(email=email, subject=subject[0:100], success=success, error=error)
    

class EmailStatistics(models.Model):
    date = models.DateField(unique=True)
    quantity = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%s' % self.date.strftime('%Y/%m/%d')


class EmailDatabase(models.Model):
    email = models.EmailField(unique=True)

    
def update_email_database(sender, instance, **kargs):
    if instance.email:
        EmailDatabase.objects.get_or_create(email=instance.email)


EMAIL_DATABASE_ACTIVATED = settings.ACTIVATE_EMAIL_DATABASE if hasattr(settings, 'ACTIVATE_EMAIL_DATABASE') else False
if EMAIL_DATABASE_ACTIVATED:
    post_save.connect(update_email_database,
                      sender=User,
                      dispatch_uid='email_manager.update_email_database')