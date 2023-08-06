from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from generic_helpers.managers import GenericRelationManager, ContentType


CONTENT_TYPE_RELATED_NAME = 'ct_set_for_%(class)s'


class GenericRelationModel(models.Model):
    ct_related_name = None

    content_type = models.ForeignKey(ContentType,
        verbose_name=_('Content type'),
        related_name=CONTENT_TYPE_RELATED_NAME)
    object_pk = models.CharField(
        verbose_name=_('Object ID'),
        max_length=255)
    content_object = generic.GenericForeignKey(
        ct_field='content_type',
        fk_field='object_pk')
    objects = GenericRelationManager()

    def __init__(self, *args, **kwargs):
        super(GenericRelationModel, self).__init__(*args, **kwargs)

        if not getattr(self, 'ct_related_name', None):
            return

        if not isinstance(self.ct_related_name, basestring):
            raise ValueError("The ct_related_name must me a string")

#        print self, "has custom related_name"

        content_type = self._meta.get_field('content_type').rel
#        print content_type, type(content_type), content_type.__dict__
        setattr(content_type, 'related_name', self.ct_related_name)

    class Meta:
        abstract = True
