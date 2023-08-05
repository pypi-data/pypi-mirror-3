from datetime import datetime

from django.contrib.admin.views.main import ChangeList
from django.template.defaultfilters import date

try:
    from django.contrib.humanize.templatetags.humanize import naturaltime
except ImportError:
    from .compat.humanize import naturaltime

CREATED = 0
MODIFIED = 1
DEFAULT_TIMESTAMP_FIELDS = ('created', 'modified')


def human_timestamp(value, fmt='SHORT_DATETIME_FORMAT'):
    '''
    Converts the given datetime value to a more readable string.

    If the delta between now and the given value is < 1 day it
    will return strings like 'a second ago', '2 hours ago' etc.

    Otherwise the datetime will be formatted according to the given
    format or ``SHORT_DATETIME_FORMAT``
    '''
    if (datetime.now() - value).days == 0:
        return naturaltime(value)
    return date(value, fmt)


class TimestampedChangelist(ChangeList):
    '''
    Custom changelist implementation that adds human readable
    timestamp fields to the list display.
    '''

    def __init__(self, *args, **kwargs):
        super(TimestampedChangelist, self).__init__(*args, **kwargs)
        self.created = self.get_created_list_display()
        self.modified = self.get_modified_list_display()
        self.add_to_list_display()

    def add_to_list_display(self):
        '''
        Appends the created and modified fields to the list display, unless
        they are already in there.
        '''
        if not self.created in self.list_display:
            self.list_display.append(self.created)
        if not self.modified in self.list_display:
            self.list_display.append(self.modified)

    def get_timestamp_name(self, created_or_modified):
        '''
        Get the accessor name as configured using the model admin's
        ``timestamp_fields`` attribute.
        '''
        return self.model_admin.timestamp_fields[created_or_modified]

    def get_timestamp_verbose_name(self, created_or_modified):
        '''
        Get the accessor name as configured using the model admin's
        ``timestamp_fields`` attribute.
        '''
        accessor = self.get_timestamp_name(created_or_modified)
        return self.model._meta.get_field(accessor).verbose_name

    def get_timestamp(self, obj, created_or_modified):
        '''
        Get either the created or modified datetime from the model.
        '''
        accessor = self.get_timestamp_name(created_or_modified)
        if hasattr(obj, accessor):
            return getattr(obj, accessor)

    def get_created_list_display(self):
        '''
        Create the `created` list_display method.
        '''
        created = lambda obj: human_timestamp(
                                self.get_timestamp(obj, CREATED))
        created.admin_order_field = self.get_timestamp_name(CREATED)
        created.short_description = self.get_timestamp_verbose_name(CREATED)
        return created

    def get_modified_list_display(self):
        '''
        Create the `modified` list_display method.
        '''
        modified = lambda obj: human_timestamp(
                                 self.get_timestamp(obj, MODIFIED))
        modified.admin_order_field = self.get_timestamp_name(MODIFIED)
        modified.short_description = self.get_timestamp_verbose_name(MODIFIED)
        return modified


class TimestampedAdminMixin(object):
    '''
    This mixin adds custom display of timestamp fields to the Django
    admin changelist.
    '''

    timestamp_fields = DEFAULT_TIMESTAMP_FIELDS

    def get_changelist(self, request, **kwargs):
        '''
        Hands back the custom changelist implementation.
        '''
        return TimestampedChangelist
