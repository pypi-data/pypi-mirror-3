from django.db import models

class AbstractFeedItem(models.Model):

    source_id = models.CharField(max_length=64, unique=True, null=True)
    source_title = models.CharField(max_length=255, null=True)
    source_url = models.URLField(null=True)
    source_description = models.TextField(null=True)
    source_author = models.CharField(max_length=255, null=True)
    source_thumbnail = models.URLField(null=True)
    source_pub_date = models.DateTimeField(null=True)
    sync_date = models.DateTimeField(auto_now=True)

    class Meta:

        abstract = True
        ordering = ['source_pub_date']
        verbose_name_plural = "Feed items"