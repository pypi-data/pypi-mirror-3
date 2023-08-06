from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^send-email-to-groups', 'email_manager.feature_send_email.send_email_to_groups', name='send_email_to_groups'),
    url('^send-email-to-users', 'email_manager.feature_send_email.send_email_to_users', name='send_email_to_users'),
    url('^update-statistics', 'email_manager.feature_update_statistics.update_statistics', name='update_statistics'),
)
