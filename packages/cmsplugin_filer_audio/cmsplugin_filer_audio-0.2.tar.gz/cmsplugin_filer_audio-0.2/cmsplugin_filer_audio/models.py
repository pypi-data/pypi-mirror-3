from django.db import models
from cms.models import CMSPlugin
from filer.fields.file import FilerFileField


class FilerAudioPlugin(CMSPlugin):
    title = models.CharField(max_length=250)
    audiofile = FilerFileField(null=True, blank=True)
    autostart = models.BooleanField(default=False)

    def __unicode__(self):
      return self.title

    def copy_relations(self, oldinstance):
        self.audiofile = oldinstance.audiofile
        self.autostart = oldinstance.autostart
