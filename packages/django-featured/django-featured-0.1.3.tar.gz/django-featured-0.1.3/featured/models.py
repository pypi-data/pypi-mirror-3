import logging
import mimetypes
import re

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_extensions.db.models import TimeStampedModel
from featured.managers import PublishedManager

log = logging.getLogger('featured.models')

class FeaturedItem(TimeStampedModel):
    published_date = models.DateTimeField(_('Published date'), default=True)
    expiration_date = models.DateTimeField(_('Expiration date'), blank=True, null=True)
    default = models.BooleanField(_('Default item'), default=False)
    photo = models.ImageField(_('Photo'), blank=True, null=True, upload_to='/featured_photos/')
    text = models.CharField(_('Text'), blank=True, null=True, max_length=200, help_text="Text to be used in place of the photo, or as a caption.")

    objects = models.Manager()
    published_objects = PublishedManager()

    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('fe-item-detail', (self.blog_set.slug, self.slug))

    class Meta:
        verbose_name=_('Featured item')
        verbose_name_plural=_('Featured items')

