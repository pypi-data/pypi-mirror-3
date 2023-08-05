# -*- coding: utf-8 -*-
from django.test import TestCase
from django_dynamic_fixture import get
from django_dynamic_fixture.ddf import BadDataError

from intruder.models import IntruderRule


class IntruderRuleTest(TestCase):

    def test_either_url_pattern_or_view_name_must_be_filled(self):
        get(IntruderRule, url_pattern='x', view_name='')
        get(IntruderRule, url_pattern='', view_name='x')
        self.assertRaises(BadDataError, get, IntruderRule, url_pattern='', view_name='')
