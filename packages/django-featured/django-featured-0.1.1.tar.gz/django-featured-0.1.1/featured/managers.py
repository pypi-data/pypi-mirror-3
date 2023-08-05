from django.db import models
from datetime import datetime

class PublishedManager(models.Manager):

    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published_date__isnull=False)


