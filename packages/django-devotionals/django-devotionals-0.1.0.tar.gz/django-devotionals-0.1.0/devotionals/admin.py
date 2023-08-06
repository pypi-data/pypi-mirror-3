import logging
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from taggit.models import Tag

from devotionals.models import Devotional

class DevotionalAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'author', )
    list_filter = ('status', )
    list_per_page = 25
    search_fields = ('title', 'body', )
    date_hierarchy = 'publish_date'

    def save_model(self, request, obj, form, change):
        """Set the devotional's author based on the logged in user and make sure at least one site is selected"""

        try:
            author = obj.author
        except User.DoesNotExist:
            obj.author = request.user

        obj.save()

        # this requires a Devotional object already
        obj.do_auto_tag('default')
        form.cleaned_data['tags'] += list(obj.tags.all())

admin.site.register(Devotional, DevotionalAdmin)
