from urllib import urlretrieve
from random import choice
from string import letters, lowercase, digits
from random import randint, randrange, random
from datetime import date, datetime, timedelta
from decimal import Decimal
from os import path, listdir
from tempfile import NamedTemporaryFile

from django.db.models import fields
from django.core.files import File
from django.core.validators import MaxLengthValidator
from django.contrib.webdesign import lorem_ipsum


def get_or_create_random(model, **kwargs):
    """
    Returns an instance of model that matches the values passed in kwargs.
    If such an instance does not exist, creates a new one, filling its fields
    with the values provided in kwargs.
    Fields that are required and are not provided with values are filled with
    random values.
    """
    defaults = kwargs.pop('defaults', {})
    objects = model.objects.filter(**kwargs).order_by('?')
    if objects:
        return objects[0]
    else:
        params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
        # Use defaults only to create an instance, not to get an existing one
        params.update(defaults)
        for field in model._meta.fields:
            if not (field.name in params or field_to_skip(field)):
                params[field.name] = fill_field(field)
        obj = model(**params)
        obj.save()
        return obj

def field_to_skip(field):
    """
    Check conditions by which a field should NOT be filled randomly.
    """
    skip = field.null or field.blank or field.has_default()
    # NOTE: The following conditions states that OneToOneField should not be
    # filled. The reason is that these fields are used for model inheritance
    # and (in that case) are automatically filled.
    # FIXME: Check if there are other cases where OneToOneField should be
    #        filled with random values
    skip = skip or (type(field) == fields.related.OneToOneField)
    return skip

def fill_field(field):
    """
    Fill a field with a random content based on its type.
    """
    internal_type = field.get_internal_type()
    try:
        return eval("random_%s(field)" % internal_type)
    except NameError:
        raise NameError, "Don't know how randomly fill a %s" % internal_type

def random_BigIntegerField(field):
    """
    Generates a random number for a BigIntegerField.
    """
    return randint(-2**63+1, 2**63)

def random_BooleanField(field):
    """
    Generates a random boolean for a BooleanField.
    """
    return bool(randint(0,1))

def random_CharField(field):
    """
    Generates random char data for a CharField.
    Satisfies the MaxLengthValidator requirement of the field.
    """
    for validator in field.validators:
        if type(validator) == MaxLengthValidator:
            limit = validator.limit_value
    if type(field) == fields.CharField:
        length = xrange(randint(1, limit))
        if field.choices:
            return choice(field.choices)[0]
        else:
            return "".join([choice(letters + digits) for i in length])
    elif type(field) == fields.CommaSeparatedIntegerField:
        length = xrange(randint(1, limit))
        return "".join([choice(digits+',') for i in length]).strip(',')
    elif type(field) == fields.EmailField:
        suffix = '@example.com' # harmless domain, avoids spamming people
        length = xrange(randint(1, (limit or 75)-len(suffix)))
        return ''.join([choice(lowercase) for i in length]) + suffix
    elif type(field) == fields.URLField:
        prefix = 'http://'
        suffix = '.example.com' # harmless domain, avoids spamming people
        length = xrange(randint(1, (limit or 200)-len(prefix)-len(suffix)))
        return prefix + ''.join([choice(lowercase) for i in length]) + suffix
    elif type(field) == fields.XMLField:
        pass # raise AssertionError, "TODO!"

def random_DateField(field):
    """
    Generates a random date for a DateField.
    By convenience, restrict to +/- 10000 days from now.
    """
    return date.today() + timedelta(randint(-10000,10000))

def random_DateTimeField(field):
    """
    Generates a random date/time for a DateTimeField.
    By convenience, restrict to +/- 10000 days from now.
    """
    return datetime.now() + timedelta(randint(-10000,10000))

def random_DecimalField(field):
    """
    Generates a random number for a DecimalField.
    Satisfies the MaxLengthValidator requirement of the field.
    """
    return Decimal(randrange(10**field.max_digits))/10**field.decimal_places

def random_FileField(field):
    """
    Find or download a random image object for a FileField.
    """
    if type(field) == fields.files.FileField:
        local_path = random_FilePathField(field)
    elif type(field) == fields.files.ImageField:
        # TODO: Get a random image from flickr instead
        remote_path="http://blazingwolf.com/drupal6/files/random%20flame.jpg"
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.close()
        local_path = tmp_file.name
        urlretrieve(remote_path, local_path)
    f = open(local_path, 'r')
    f.read()
    # TODO: Close the file at the end
    return File(f)

def random_FilePathField(field):
    """
    Picks a random file path for a FilePathField.
    If a path is not specified, picks a file path from the current folder.
    """
    if hasattr(field, 'path'):
        folder = field.path
    else:
        folder = "."
    return choice([f for f in listdir(folder)
        if path.isfile(path.join(folder, f))])

def random_FloatField(field):
    """
    Generates a random float for a FloatField.
    By convenience, restrict to +/- 10^10.
    """
    return random()*10**randrange(-10,10)

def random_IntegerField(field):
    """
    Generates a random number for an IntegerField.
    """
    return randint(-2**31+1, 2**31)

def random_IPAddressField(field):
    """
    Generates a random IP Address for an IPAddressField.
    """
    return ".".join([str(randrange(0,255)) for i in xrange(4)])

def random_PositiveIntegerField(field):
    """
    Generates a random positive number for an PositiveIntegerField.
    """
    return randint(0, 2**31)

def random_PositiveSmallIntegerField(field):
    """
    Generates a random positive number for an PositiveSmallIntegerField.
    """
    return randint(0, 2**31)

def random_SlugField(field):
    """
    Generates random char data for a SlugField.
    Satisfies the MaxLengthValidator requirement of the field if present.
    """
    for validator in field.validators:
        if type(validator) == MaxLengthValidator:
            limit = validator.limit_value
    length = xrange(randint(1, (limit or 50)))
    return "".join([choice(lowercase) for i in length])

def random_SmallIntegerField(field):
    """
    Generates a random number for a SmallIntegerField.
    """
    return randint(-2**31+1, 2**31)

def random_TextField(field):
    """
    Generates a random number of paragraphs (maximum: 5) for a TextField.
    """
    limit = randint(1, 5)
    return "\n".join(lorem_ipsum.paragraphs(2, False))

def random_ForeignKey(field):
    """
    Find or generate a random related object for a ForeignKey.
    """
    return get_or_create_random(field.related.parent_model)

