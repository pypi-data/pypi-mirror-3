from datetime import datetime
from django.template.defaultfilters import slugify

def create_date(sender, instance, **kwargs):
    if not instance.created:
        instance.created = datetime.now()


def slugify_name(sender, instance, **kwargs):
    instance.name = slugify(instance.name)
