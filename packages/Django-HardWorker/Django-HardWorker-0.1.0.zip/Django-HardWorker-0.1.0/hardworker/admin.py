from django.contrib import admin
from models import *


class HardJobAdmin(admin.ModelAdmin):
    """

    """
    list_filter = ('owner', 'app', 'worker', 'successful', 'owner_notified',)
    list_display = ('owner', 'app', 'worker', 'registration_date','started', 'finished', 'successful', 'progress', 'owner_notified',)
    ordering = ('-registration_date',)
    exclude = ('owner',)

    def save_model(self, request, obj, form, change):
        """

        """
        obj.owner = request.user
        if not obj.id:
            super(HardJob, obj).save()

        super(HardJob, obj).save()


admin.site.register(HardJob, HardJobAdmin)