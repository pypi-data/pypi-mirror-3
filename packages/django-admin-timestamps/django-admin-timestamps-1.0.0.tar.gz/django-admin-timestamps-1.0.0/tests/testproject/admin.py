from django.contrib import admin
from models import TimestampedItem, FakeTimestampedItem,\
    AlternativeTimestampedItem
from admintimestamps import TimestampedAdminMixin


class TimestampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(TimestampedItem, TimestampedAdmin)
admin.site.register(FakeTimestampedItem, TimestampedAdmin)


class AlternativeTimestampedAdmin(TimestampedAdmin):
    timestamp_fields = ('created_at', 'modified_at')

admin.site.register(AlternativeTimestampedItem, AlternativeTimestampedAdmin)
