import logging
import mimetypes
import re

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from taggit.managers import TaggableManager
from taggit.models import Tag
from devotional.decorators import logtime, once_per_instance
from markup_mixin.models import MarkupMixin
from django_extensions.db.models import TitleSlugDescriptionModel
from django.template.defaultfilters import slugify, striptags

from devotionals.managers import PublishedPostManager

log = logging.getLogger('devotional.models')

class Devotional(TimeStampedModel):
    body = models.TextField(_('Body'))
    publish_date = models.DateTimeField(_('Publish date'), default=datetime.now())
    published = models.BooleanField(_('Published'), default=True)
    author = models.ForeignKey(Author, blank=True, null=True)
    related_devotionals = models.ManyToManyField('self', blank=True)
    word_count=models.IntegerField(_('Word count'), blank=True, null=True)
    relatable_words=models.TextField(_('Relatable words'), blank=True, null=True)
    tags = TaggableManager()

    objects = models.Manager()
    published_objects = PublishedDevotionalManager()

    def save(self, *args, **kwargs):
        super(Devotional, self).save()

        requires_save = self._count_words()
        requires_save |= self._find_related()

        if requires_save:
            # bypass the other processing
            super(Devotional, self).save()

    def _count_words(self):
        self.word_count = self.body.split(' ')
        return self.word_count()

    def _find_related(self):
        big_words_found=[]
        words = self.body.split(' ')

        for word in words:
            if len(word) > 6:
                big_words_found+=word
        if big_words_found:
            self.relatable_words = ','.join(big_words_found)
            return True
        else:
            return False
                
    @models.permalink
    def get_absolute_url(self):
        return ('mb-devotional-detail', (self.publish_date.year, self.publish_date.month, self.publish_date.day))

