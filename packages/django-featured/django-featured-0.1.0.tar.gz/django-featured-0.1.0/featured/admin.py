import logging
from django.conf import settings
from django.contrib import admin
from featured.models import FeaturedItem

admin.site.register(FeaturedItem)
