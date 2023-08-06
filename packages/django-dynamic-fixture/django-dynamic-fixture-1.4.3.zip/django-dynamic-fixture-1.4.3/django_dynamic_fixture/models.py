# -*- coding: utf-8 -*-

from django.db import models

class EmptyModel(models.Model):
    pass


class ModelWithNumbers(models.Model):
    #id is a models.AutoField()
    integer = models.IntegerField(null=True, unique=True)
    smallinteger = models.SmallIntegerField(null=True, unique=True)
    positiveinteger = models.PositiveIntegerField(null=True, unique=True)
    positivesmallinteger = models.PositiveSmallIntegerField(null=True, unique=True)
    biginteger = models.BigIntegerField(null=True, unique=True)
    float = models.FloatField(null=True, unique=True)
    decimal = models.DecimalField(max_digits=2, decimal_places=1, null=True, unique=False)

class ModelWithStrings(models.Model):
    string = models.CharField(max_length=1, null=True, unique=True)
    text = models.TextField(null=True, unique=True)
    slug = models.SlugField(null=True, unique=True)
    commaseparated = models.CommaSeparatedIntegerField(max_length=100, null=True, unique=True)

class ModelWithBooleans(models.Model):
    boolean = models.BooleanField()
    nullboolean = models.NullBooleanField()

class ModelWithDateTimes(models.Model):
    date = models.DateField(null=True, unique=True)
    datetime = models.DateTimeField(null=True, unique=True)
    time = models.TimeField(null=True, unique=True)


class ModelWithFieldsWithCustomValidation(models.Model):
    email = models.EmailField(null=True, unique=True)
    url = models.URLField(null=True, unique=True)
    ip = models.IPAddressField(null=True, unique=False)
    xml = models.XMLField(null=True, unique=True)


class ModelWithFileFields(models.Model):
    filepath = models.FilePathField(unique=True, blank=True)
    file = models.FileField(upload_to='.')

    try:
        import pil
        # just test it if the PIL package is installed
        image = models.ImageField(upload_to='.')
    except ImportError:
        pass


class ModelWithDefaultValues(models.Model):
    integer_with_default = models.IntegerField(null=True, default=3)
    string_with_choices = models.CharField(max_length=5, null=True, choices=(('a', 'A'), ('b', 'B')))
    string_with_choices_and_default = models.CharField(max_length=5, null=True, default='b', choices=(('a', 'A'), ('b', 'B')))
    foreign_key_with_default = models.ForeignKey('EmptyModel', null=True, default=None)


class ModelWithRelationships(models.Model):
    # relationship
    selfforeignkey = models.ForeignKey('self', null=True)
    foreignkey = models.ForeignKey('ModelRelated', related_name='fk', null=True)
    onetoone = models.OneToOneField('ModelRelated', related_name='o2o', null=True)
    manytomany = models.ManyToManyField('ModelRelated', related_name='m2m')

    integer = models.IntegerField(null=True, unique=True)

    # generic field
    # TODO

class ModelRelated(models.Model):
    integer = models.IntegerField(null=True)

class ModelWithCyclicDependency(models.Model):
    d = models.ForeignKey('ModelWithCyclicDependency2', null=True)

class ModelWithCyclicDependency2(models.Model):
    c = models.ForeignKey(ModelWithCyclicDependency, null=True)


class ModelAbstract(models.Model):
    integer = models.IntegerField(null=True, unique=True)

    class Meta:
        abstract = True

class ModelParent(ModelAbstract):
    pass

class ModelChild(ModelParent):
    pass

class ModelChildWithCustomParentLink(ModelParent):
    my_custom_ref = models.OneToOneField(ModelParent, parent_link=True, related_name='my_custom_ref_x')

class ModelWithRefToParent(models.Model):
    parent = models.ForeignKey(ModelParent)


class CustomDjangoField(models.IntegerField):
    pass

class NewField(models.Field):
    pass

class ModelWithCustomFields(models.Model):
    x = CustomDjangoField(null=False)
    y = NewField(null=True)

class ModelWithUnsupportedField(models.Model):
    z = NewField(null=False)


class ModelForNullableTest(models.Model):
    nullable = models.IntegerField(null=True)
    not_nullable = models.IntegerField(null=False)


class ModelForIgnoreListTest(models.Model):
    required = models.IntegerField(null=False)
    required_with_default = models.IntegerField(null=False, default=1)
    not_required = models.IntegerField(null=True)
    not_required_with_default = models.IntegerField(null=True, default=1)
    self_reference = models.ForeignKey('ModelForIgnoreListTest', null=True)
    different_reference = models.ForeignKey(ModelForNullableTest, null=True)

