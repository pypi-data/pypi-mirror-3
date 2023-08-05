# -*- coding: utf-8 -*-
from django.contrib import admin
from intruder.models import UrlIntruderRule, ViewIntruderRule
from django import forms


class IntruderRuleAdminForm(forms.ModelForm):

    def validate_view_path_exists(self, lookup_view):
        from django.core import urlresolvers
        try:
            lookup_view = lookup_view.encode('ascii')
            mod_name, func_name = urlresolvers.get_mod_func(lookup_view)
            lookup_view = getattr(urlresolvers.import_module(mod_name), func_name)
            if not callable(lookup_view):
                raise forms.ValidationError("'%s.%s' is not a callable." % (mod_name, func_name))
        except ImportError, e:
            mod_name, _ = urlresolvers.get_mod_func(lookup_view)
            raise forms.ValidationError("Could not import %s. Error was: %s" % (mod_name, str(e)))
        except AttributeError, e:
            mod_name, func_name = urlresolvers.get_mod_func(lookup_view)
            raise forms.ValidationError("Tried %s in module %s. Error was: %s" % (func_name, mod_name, str(e)))

    def clean_redirect_view(self):
        self.validate_view_path_exists(self.cleaned_data['redirect_view'])
        return self.cleaned_data['redirect_view']


class ViewIntruderRuleAdminForm(IntruderRuleAdminForm):
    class Meta:
        model = ViewIntruderRule

    def can_not_set_an_intruder_view(self, lookup_view):
        if lookup_view.startswith('intruder.views'):
            raise forms.ValidationError('Can not select an Intruder\'s view')

    def clean_view_name(self):
        self.validate_view_path_exists(self.cleaned_data['view_name'])
        self.can_not_set_an_intruder_view(self.cleaned_data['view_name'])
        return self.cleaned_data['view_name']

    def clean(self):
        # if there is a validation error in the view_name, it would raise an KeyError
        if 'view_name' in self.cleaned_data and 'redirect_view' in self.cleaned_data and \
            self.cleaned_data['view_name'] == self.cleaned_data['redirect_view']:
            raise forms.ValidationError('Redirect view is equal to the selected view.')
        return self.cleaned_data


class UrlIntruderRuleAdminForm(IntruderRuleAdminForm):
    class Meta:
        model = UrlIntruderRule


class ViewIntruderRuleAdmin(admin.ModelAdmin):
    form = ViewIntruderRuleAdminForm
    list_display = ('id', 'view_name', 'redirect_view', 'super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule')
    list_filter = ('super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule',)
    ordering = ('view_name',)
    search_fields = ('view_name',)


class UrlIntruderRuleAdmin(admin.ModelAdmin):
    form = UrlIntruderRuleAdminForm
    list_display = ('id', 'url_pattern', 'redirect_view', 'super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule')
    list_filter = ('super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule',)
    ordering = ('url_pattern',)
    search_fields = ('url_pattern',)


admin.site.register(ViewIntruderRule, ViewIntruderRuleAdmin)
admin.site.register(UrlIntruderRule, UrlIntruderRuleAdmin)

#Useful for development
from django.contrib.auth.models import Permission
admin.site.register(Permission)
