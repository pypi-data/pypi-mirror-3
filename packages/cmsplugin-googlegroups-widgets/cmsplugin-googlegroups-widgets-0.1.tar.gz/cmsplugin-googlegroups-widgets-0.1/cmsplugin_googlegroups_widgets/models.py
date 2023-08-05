from cms.models.pluginmodel import CMSPlugin
from django.db import models

class GoogleGroup(models.Model):
    group_name = models.CharField(max_length=300)

    def __unicode__(self):
        return unicode(self.group_name)

class GGSubscribe(CMSPlugin):
    group = models.ForeignKey(GoogleGroup)

    def __unicode__(self):
        return unicode(self.group)

    def __str__(self):
        return self.group.group_name


