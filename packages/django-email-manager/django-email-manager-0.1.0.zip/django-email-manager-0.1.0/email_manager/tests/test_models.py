# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User

from django.test import TestCase
from django_dynamic_fixture import G

from email_manager.models import EmailLog


class EmailLogTest(TestCase):
    
    def test_must_truncate_long_subjects(self):
        log = EmailLog.create_log('x@x.net', 'x' * 101, success=True, error=None)
        self.assertEquals('x' * 100, log.subject)

    def test_must_ignore_error_in_case_of_success(self):
        log = EmailLog.create_log('x@x.net', 'x', success=True, error='x')
        self.assertEquals(None, log.error)
        
    def test_must_not_ignore_error_in_case_of_error(self):
        log = EmailLog.create_log('x@x.net', 'x', success=False, error='x')
        self.assertEquals('x', log.error)
        
    def test_must_truncate_long_error_messages(self):
        log = EmailLog.create_log('x@x.net', 'x', success=False, error='x' * 256)
        self.assertEquals('x' * 255, log.error)