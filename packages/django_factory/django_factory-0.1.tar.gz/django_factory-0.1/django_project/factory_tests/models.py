from django.core import exceptions
from django.db import models


class ModelWithNoFields(models.Model):
    pass


class ModelWithCharField(models.Model):

    char_field = models.CharField(max_length=100)


class ModelWithNullCharField(models.Model):

    char_field = models.CharField(max_length=100, null=True, blank=True)


class ModelWithNullCharFieldAndFactory(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100, null=True, blank=True)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithNullCharFieldAndFactory.VALUE


class ModelWithDefaultCharField(models.Model):

    DEFAULT = 'foo'

    char_field = models.CharField(max_length=100, default=DEFAULT)


class ModelWithDefaultCharFieldAndFactory(models.Model):

    VALUE = 'bar'
    DEFAULT = 'foo'

    char_field = models.CharField(max_length=100, default=DEFAULT)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithDefaultCharFieldAndFactory.VALUE


class ModelWithCallableDefaultCharField(models.Model):

    DEFAULT = 'foo'

    def get_default():
        return ModelWithCallableDefaultCharField.DEFAULT

    char_field = models.CharField(max_length=100, default=get_default)


class ModelWithTextField(models.Model):

    text_field = models.TextField(max_length=100)


class ModelWithSlugField(models.Model):

    slug_field = models.SlugField(max_length=100)


class ModelWithBooleanField(models.Model):

    bool_field = models.BooleanField()


class ModelWithNullBooleanField(models.Model):

    bool_field = models.NullBooleanField()


class ModelWithIntegerField(models.Model):

    int_field = models.IntegerField()


if getattr(models, 'BigIntegerField', None) is not None:
    class ModelWithBigIntegerField(models.Model):

        big_int_field = models.BigIntegerField()


class ModelWithSmallIntegerField(models.Model):

    small_int_field = models.SmallIntegerField()


class ModelWithPositiveIntegerField(models.Model):

    positive_int_field = models.PositiveIntegerField()


class ModelWithPositiveSmallIntegerField(models.Model):

    positive_small_int_field = models.PositiveSmallIntegerField()


class ModelWithFloatField(models.Model):

    float_field = models.FloatField()


class ModelWithDecimalField(models.Model):

    decimal_field = models.DecimalField(decimal_places=2, max_digits=3)


class ModelWithDateField(models.Model):

    date_field = models.DateField()


class ModelWithDateTimeField(models.Model):

    datetime_field = models.DateTimeField()


class ModelWithTimeField(models.Model):

    time_field = models.TimeField()


class ModelWithURLField(models.Model):

    url_field = models.URLField()


class ModelWithEmailField(models.Model):

    email_field = models.EmailField()


class ModelWithCommaSeparatedIntegerField(models.Model):

    csi_field = models.CommaSeparatedIntegerField(max_length=6)


class ModelWithIPAddressField(models.Model):

    ip_field = models.IPAddressField()


if getattr(models, 'GenericIPAddressField', None) is not None:
    class ModelWithGenericIPAddressField(models.Model):

        ip_field = models.GenericIPAddressField()


class ModelWithChoices(models.Model):

    CHOICES = [(-1, 'foo'), (-2, 'bar')]

    choices_field = models.IntegerField(choices=CHOICES)


class ModelWithFieldGenerator(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100)

    class Factory:

        @staticmethod
        def get_char_field(field, factory):
            return ModelWithFieldGenerator.VALUE


class ModelWithInstanceGenerator(models.Model):

    VALUE = 'bar'

    char_field = models.CharField(max_length=100)

    class Factory:

        @staticmethod
        def make_instance(factory, char_field=None):
            if char_field is None:
                char_field = ModelWithInstanceGenerator.VALUE
            return ModelWithInstanceGenerator(char_field=char_field)


class ModelReferencedByManyToManyField(models.Model):
    pass


class ModelWithManyToManyField(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField)


class ModelWithManyToManyFieldAndFactory(models.Model):

    VALUE = ModelReferencedByManyToManyField()

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:

        @staticmethod
        def get_things(field, factory):
            return [ModelWithManyToManyFieldAndFactory.VALUE]


class ModelWithNullManyToManyField(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField, null=True)


class ModelWithNullManyToManyFieldAndFactory(models.Model):

    VALUE = ModelReferencedByManyToManyField()

    things = models.ManyToManyField(ModelReferencedByManyToManyField, null=True)

    class Factory:

        @staticmethod
        def get_things(field, factory):
            return [ModelWithNullManyToManyFieldAndFactory.VALUE]


class ModelWithSelfManyToManyField(models.Model):

    # Not symetrical so we can tell which is the child
    things = models.ManyToManyField('self', symmetrical=False)


class ModelWithCircularReferenceLoop1(models.Model):

    things = models.ManyToManyField('ModelWithCircularReferenceLoop2')


class ModelWithCircularReferenceLoop2(models.Model):

    other_things = models.ManyToManyField('ModelWithCircularReferenceLoop1')


class ModelWantingTwoManyToManyInstances(models.Model):

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:
        number_of_things = 2


class ModelWithCallableSpecifiedManyToManyField(models.Model):

    COUNT = 2

    things = models.ManyToManyField(ModelReferencedByManyToManyField)

    class Factory:

        @staticmethod
        def number_of_things():
            return ModelWithCallableSpecifiedManyToManyField.COUNT


class ModelReferencedByForiegnKeyField(models.Model):
    pass


class ModelWithForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField)


class ModelWithNullAndBlankForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, null=True, blank=True)


class ModelWithNullForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, null=True)


class ModelWithBlankForeignKey(models.Model):

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField, blank=True)


class ModelWithForeignKeyAndFactory(models.Model):

    VALUE = ModelReferencedByForiegnKeyField()

    thing = models.ForeignKey(ModelReferencedByForiegnKeyField)

    class Factory:

        @staticmethod
        def get_thing(field, factory):
            return ModelWithForeignKeyAndFactory.VALUE


class ModelWithSelfForeignKey(models.Model):

    thing = models.ForeignKey('self', null=True, blank=True)


class ModelWithCircularForiegnKeyReferenceLoop1(models.Model):

    thing = models.ForeignKey('ModelWithCircularForiegnKeyReferenceLoop2')


class ModelWithCircularForiegnKeyReferenceLoop2(models.Model):

    thing = models.ForeignKey('ModelWithCircularForiegnKeyReferenceLoop1', null=True, blank=True)


if getattr(models.CharField, 'validators', None) is not None:
    class ModelWithImpossibleValidator(models.Model):

        def impossible(value):
            raise exceptions.ValidationError('Impossible')

        char_field = models.CharField(max_length=100, validators=[impossible])
