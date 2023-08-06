from django.db import models
from django.contrib.contenttypes.models import ContentType

class GenericQuerySet(models.query.QuerySet):
    def _filter_or_exclude(self, negate, *args, **kwargs):
        if 'content_object' in kwargs:
            if not isinstance(kwargs['content_object'], models.Model):
                raise ValueError, 'content_object must be a Model instance'

            instance = kwargs.pop('content_object')

            kwargs['content_type'] = ContentType.objects.get_for_model(instance)
            kwargs['object_pk']    = instance.pk

        return super(GenericQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

    def get_for_object(self, object):
        return self.select_related().filter(content_object=object)

    def get_for_model(self, model):
        return self.select_related().filter(
            content_type=ContentType.objects.get_for_model(model)
        )

class GenericRelationManager(models.Manager):
    def get_query_set(self):
        return GenericQuerySet(self.model)

    def get_for_object(self, object):
        return self.get_query_set().select_related().\
            filter(
                content_type = ContentType.objects.get_for_model(object),
                object_pk    = object.pk,
            )

    def get_for_model(self, model):
        return self.get_query_set().select_related().\
            filter(content_type=ContentType.objects.get_for_model(model)
        )