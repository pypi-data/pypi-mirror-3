from django.db import models
from ccstraps import listeners

class Strap(models.Model):
    name = models.SlugField(
            unique=True,
            max_length=20)
    delay = models.PositiveSmallIntegerField(
            blank=True,
            null=True,
            default=1000)
    created = models.DateTimeField(
            blank=True,
            null=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s' % self.name


class StrapImage(models.Model):
    strap = models.ForeignKey(Strap)
    src = models.ImageField(
            upload_to='ccstraps/%Y/%m/%d')
    url = models.CharField(
            max_length=255,
            blank=True,
            null=True)
    caption = models.CharField(
            max_length=255,
            blank=True,
            null=True)
    order = models.DecimalField(
            decimal_places=2,
            max_digits=8,
            default='5.00')

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'%s' % self.pk


models.signals.pre_save.connect(
        listeners.create_date,
        sender=Strap,
        dispatch_uid='strap_create_date')
models.signals.pre_save.connect(
        listeners.slugify_name,
        sender=Strap,
        dispatch_uid='strap_slugify_name')
