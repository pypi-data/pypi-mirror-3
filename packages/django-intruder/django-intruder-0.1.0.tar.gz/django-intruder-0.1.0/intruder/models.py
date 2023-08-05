# -*- coding: utf-8 -*-
import re

from django.core.cache import cache
from django.db import models
from django.db.utils import IntegrityError


class IntruderRuleManager(models.Manager):
    CACHE_KEY = 'IntruderRules'

    def cached_rules(self):
        rules = cache.get(IntruderRuleManager.CACHE_KEY)
        if rules is None:
            rules = self.all()
            cache.set(IntruderRuleManager.CACHE_KEY, rules)
        return dict([(rule.view_name, rule) for rule in rules])

    def clear_cache(self):
        cache.delete(IntruderRuleManager.CACHE_KEY)

    def get_first_rule_that_matches_this_url(self, path):
        rules = self.cached_rules().values()
        for rule in rules:
            if re.match(rule.url_pattern, path):
                return rule

    def get_first_rule_that_matches_this_view_name(self, view_name):
        try:
            return self.cached_rules()[view_name]
        except KeyError:
            pass


class IntruderRule(models.Model):
    PERMISSION_KEY = u'intruder.can_use_this_feature'

    url_pattern = models.CharField(max_length=200, unique=True, db_index=True, blank=True, null=True,
                                   help_text='Example: /myapp')

    view_name = models.CharField(max_length=300, unique=True, db_index=True, blank=True, null=True,
                                 help_text='Text format: app_name.views.view_name. Examples: intruder.views.'
                                 'feature_under_maintenance or intruder.views.feature_is_no_longer_available')

    redirect_view = models.CharField(max_length=300, default='intruder.views.feature_under_maintenance',
                                     help_text='If the view no longer exist, this rule will be ignored.')

    # Who can ignore this rule
    super_user_can_ignore_this_rule = models.BooleanField(default=True)
    user_with_permission_can_ignore_this_rule = models.BooleanField(default=True,
                                                                    help_text='Permission name: intruder | intruder rule | can_use_this_feature')

    objects = IntruderRuleManager()

    class Meta:
        permissions = ((u'can_use_this_feature', u'Can use this feature'),)

    def __unicode__(self):
        return '"%s" or "%s" => %s' % (self.url_pattern, self.view_name, self.redirect_view)

    def save(self, **kwargs):
        if not self.url_pattern and not self.view_name:
            raise IntegrityError('Either url_pattern or view_name must be filled.')
        super(IntruderRule, self).save(**kwargs)
        IntruderRule.objects.clear_cache()
