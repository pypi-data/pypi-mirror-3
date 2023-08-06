from django.db import models
from django.core.management import call_command
from generic_helpers.models import GenericRelationModel


FOO_NUMBER = 3
BAR_NUMBER = 3
BAZ_CT_REL = 'buzz'

class Foo(models.Model):
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'


class Bar(GenericRelationModel):
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'


class Baz(GenericRelationModel):
    ct_related_name = BAZ_CT_REL
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'


class BadBaz(GenericRelationModel):
    ct_related_name = 31337
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'


def load_test_data():
    for i in xrange(1, FOO_NUMBER + 1):
        foo = Foo.objects.create(title='Foo #{0}'.format(i))

        for j in xrange(1, BAR_NUMBER + 1):
            Bar.objects.create(title='Bar #{0}'.format(j),
                content_object=foo)
            Baz.objects.create(title='Baz #{0}'.format(j),
                content_object=foo)


call_command('syncdb',
    interactive=False,
    verbosity=0)
