import logging
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User

from isitup.models import Service, ServiceCheck, ServiceOutage

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'path', 'owner', )
    list_filter = ('host', )
    list_per_page = 25
    search_fields = ('title', 'description', )

    def save_model(self, request, obj, form, change):
        """Set the service's owner based on the logged in user """

        try:
            owner = obj.owner
        except User.DoesNotExist:
            obj.owner = request.user

        obj.save()

admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceCheck)
admin.site.register(ServiceOutage)
