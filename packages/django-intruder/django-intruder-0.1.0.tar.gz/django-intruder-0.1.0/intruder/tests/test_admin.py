# -*- coding: utf-8 -*-

from django.test import TestCase
from intruder.admin import IntruderRuleAdminForm


class IntruderRuleAdminFormTest(TestCase):

    def test_success_case(self):
        form = IntruderRuleAdminForm({'url_pattern': '/x',
                                      'view_name': 'example.views.view_a',
                                      'redirect_view': 'example.views.view_b'})
        self.assertEquals(True, form.is_valid())

    def test_url_pattern_or_view_name_must_be_filled(self):
        form = IntruderRuleAdminForm({'url_pattern': '',
                                      'view_name': '',
                                      'redirect_view': 'example.views.view_b'})
        self.assertEquals(False, form.is_valid())
        self.assertEquals('Either url_pattern or view_name must be filled.', form.errors.values()[0][0])

    def test_view_name_must_be_valid(self):
        form = IntruderRuleAdminForm({'url_pattern': 'x',
                                      'view_name': 'example.views.inexistent_view',
                                      'redirect_view': 'example.views.view_b'})
        self.assertEquals(False, form.is_valid())

    # important test to avoid errors in the method 'clean'
    def test_view_name_must_be_valid_event_if_url_pattern_is_blank(self):
        form = IntruderRuleAdminForm({'url_pattern': '',
                                      'view_name': 'example.views.inexistent_view',
                                      'redirect_view': 'example.views.view_b'})
        self.assertEquals(False, form.is_valid())

    def test_redirect_view_must_be_valid(self):
        form = IntruderRuleAdminForm({'url_pattern': '',
                                      'view_name': 'example.views.view_a',
                                      'redirect_view': 'example.views.inexistent_view'})
        self.assertEquals(False, form.is_valid())
