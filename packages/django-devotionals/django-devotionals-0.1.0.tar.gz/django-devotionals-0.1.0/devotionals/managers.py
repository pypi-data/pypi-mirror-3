from django.db import models
from datetime import datetime

class PublishedManager(models.Manager):

    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

class PublishedDevotionalManager(models.Manager):
    def get_query_set(self):
        now = datetime.now()
        return super(PublishedDevotionalManager, self).get_query_set().filter(publish_date__lte=now, is_active=True)

