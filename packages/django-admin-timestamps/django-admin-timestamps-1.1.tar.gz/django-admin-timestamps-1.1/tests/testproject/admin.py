from django.contrib import admin
from models import TimestampedItem, FakeTimestampedItem,\
    AlternativeTimestampedItem, SingleTimestampedItem, DateStampedItem
from admintimestamps import TimestampedAdminMixin


class TimestampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(TimestampedItem, TimestampedAdmin)
admin.site.register(FakeTimestampedItem, TimestampedAdmin)


class SingleTimestampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    timestamp_fields = ('modified',)

admin.site.register(SingleTimestampedItem, SingleTimestampedAdmin)


class DateStampedAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(DateStampedItem, DateStampedAdmin)


class AlternativeTimestampedAdmin(TimestampedAdmin):
    timestamp_fields = ('created_at', 'modified_at')

admin.site.register(AlternativeTimestampedItem, AlternativeTimestampedAdmin)
