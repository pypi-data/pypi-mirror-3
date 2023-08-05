# -*- coding: utf-8 -*-
from django.contrib import admin
from intruder.models import IntruderRule
from django import forms


class IntruderRuleAdminForm(forms.ModelForm):
    class Meta:
        model = IntruderRule

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

    def clean_view_name(self):
        if self.cleaned_data['view_name']: # this field is not required
            self.validate_view_path_exists(self.cleaned_data['view_name'])
        return self.cleaned_data['view_name']

    def clean_redirect_view(self):
        self.validate_view_path_exists(self.cleaned_data['redirect_view'])
        return self.cleaned_data['redirect_view']

    def clean(self):
        # if there is a validation error in the view_name, it would raise an KeyError
        view_name_not_filled = ('view_name' in self.cleaned_data and not self.cleaned_data['view_name'])
        if not self.cleaned_data['url_pattern'] and view_name_not_filled:
            raise forms.ValidationError('Either url_pattern or view_name must be filled.')
        return self.cleaned_data


class IntruderRuleAdmin(admin.ModelAdmin):
    form = IntruderRuleAdminForm
    list_display = ('url_pattern', 'view_name', 'super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule')
    list_filter = ('super_user_can_ignore_this_rule', 'user_with_permission_can_ignore_this_rule',)
    ordering = ('url_pattern', 'view_name')
    search_fields = ('url_pattern', 'view_name')


admin.site.register(IntruderRule, IntruderRuleAdmin)

# Useful for development
# from django.contrib.auth.models import Permission
# admin.site.register(Permission)
