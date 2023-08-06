import datetime

from django.db import models

class MiseryIP(models.Model):
    ip = models.GenericIPAddressField(primary_key = True, unpack_ipv4 = True)
    date_added = models.DateTimeField('date entered the database', default = datetime.datetime.now)
    notes = models.CharField(max_length = 100, blank = True)
    
    def __unicode__(self):
        return 'Misery IP: %s' % self.ip

    class Meta:
        verbose_name = 'IP v4/v6 to put in misery'
        verbose_name_plural = 'IP v4/v6 to put in misery'

