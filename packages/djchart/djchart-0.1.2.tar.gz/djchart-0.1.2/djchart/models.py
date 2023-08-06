from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

class Chart(models.Model):
    """Chart"""
    options = models.TextField(blank=True)
    data_provider = models.CharField(max_length=65535)
    auth_required = models.BooleanField(
        default=False, verbose_name=_('authorisation required'))
    data_cache_period = models.PositiveIntegerField(
        default=0, verbose_name=_('data cache period in seconds'),
        help_text=_('0 &mdash; no cache'))
    data_cache = models.TextField(blank=True, null=True)
    data_cache_datetime = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'djchart'
    
    def is_data_caching_enabled(self):
        return 0 != self.data_cache_period
    
    def is_data_cache_empty(self):
        return '' == self.data_cache
    
    def set_data_cache(self, data):
        self.data_cache = data
        self.data_cache_datetime = datetime.now()
    
    def is_data_cache_valid(self):
        if not self.is_data_caching_enabled() \
                or not self.data_cache_datetime \
                or '' == self.data_cache:
            return False
        now = datetime.now()
        cache_ends = self.data_cache_datetime + timedelta(seconds=self.data_cache_period)
        return cache_ends >= now

def invalidate_charts_data_cache(modeladmin, request, queryset):
    queryset.update(data_cache='')
invalidate_charts_data_cache.short_description = _("Invalidate data cache")

class ChartAdmin(admin.ModelAdmin):
    """Chart admin class"""
    fieldsets = (
        (None, {
            'fields': ('data_provider', 'auth_required', 'options'),
        }),
        (_('Cache'), {
            'classes': ('collapse',),
            'fields':
                ('data_cache_period', 'data_cache_datetime', 'data_cache'),
        })
    )
    actions = [invalidate_charts_data_cache]

admin.site.register(Chart, ChartAdmin)
