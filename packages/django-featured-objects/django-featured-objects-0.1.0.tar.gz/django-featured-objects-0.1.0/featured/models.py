from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Featured(models.Model):
    content_object = generic.GenericForeignKey()
    content_type = models.ForeignKey(ContentType)
    category = models.ForeignKey('Category')
    object_id = models.IntegerField()

    def __unicode__(self):
        return ('%s' % self.pk)


class Category(models.Model):
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.slug


def get_featured_queryset_for(model, category=None):
    ct = ContentType.objects.get_for_model(model)
    queryset = Featured.objects.filter(content_type=ct)
    if category:
        queryset = queryset.filter(category=category)

    return model.objects.filter(pk__in=queryset.values('object_id'))
