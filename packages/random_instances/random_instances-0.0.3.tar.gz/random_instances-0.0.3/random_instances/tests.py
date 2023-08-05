"""Unit tests for random_instances."""

from django.test import TestCase
from django.db import models
from random_instances import get_or_create_random
from unittest import skipUnless

def _isPILInstalled():
    '''Only run ImageField tests if PIL is installed'''
    try:
        import PIL
        return True
    except ImportError:
        return False

class TestingModel(models.Model):
    MAX_LENGTH           = 255
    MAX_DIGITS           = 10
    DECIMAL_PLACES       = 5
    CHOICES              = (('1', 'First'), ('2', 'Second'),)
    LOCAL_FOLDER         = "."

    big_field            = models.BigIntegerField()
    boolean_field        = models.BooleanField()
    char_field           = models.CharField(max_length=MAX_LENGTH)
    choice_field         = models.CharField(max_length=1, choices=CHOICES)
    commaseparated_field = models.CommaSeparatedIntegerField(
                            max_length=MAX_LENGTH)
    date_field           = models.DateField()
    datetime_field       = models.DateTimeField()
    decimal_field        = models.DecimalField(max_digits=MAX_DIGITS,
                            decimal_places=DECIMAL_PLACES)
    email_field          = models.EmailField()
    file_field           = models.FileField(upload_to=LOCAL_FOLDER)
    filepath_field       = models.FilePathField(path=LOCAL_FOLDER)
    float_field          = models.FloatField()
    if _isPILInstalled():
        image_field      = models.ImageField(upload_to=LOCAL_FOLDER)
    integer_field        = models.IntegerField()
    ipaddress_field      = models.IPAddressField()
    nullboolean_field    = models.NullBooleanField()
    positive_field       = models.PositiveIntegerField()
    positivesmall_field  = models.PositiveSmallIntegerField()
    slug_field           = models.SlugField()
    small_field          = models.SmallIntegerField()
    text_field           = models.TextField()
    url_field            = models.URLField()
    xml_field            = models.XMLField(schema_path=LOCAL_FOLDER)
    # TODO: add fields with default, blank, null values

class CreateRandomInstancesTestCase(TestCase):
    '''Tests the cases when get_or_create_random creates an instance.'''

    def _pre_setup(self):
        self.model_test = get_or_create_random(TestingModel)
        return super(CreateRandomInstancesTestCase, self)._pre_setup()

    def testSaveModel(self):
        """Tests that all required fields are randomly filled."""
        self.assertNotEquals(self.model_test.id, None)

    def testCharField(self):
        """Tests that a random instance has a proper CharField."""
        self.assertNotEquals(self.model_test.char_field, None)
        # TODO: check max_length

    def testChoiceField(self):
        """Tests that a random instance has a proper CharField with choices."""
        self.assertNotEquals(self.model_test.choice_field, None)
        choices = [k for k, v in self.model_test.CHOICES]
        self.assertIn(self.model_test.choice_field, choices)

    def testCommaSeparatedIntegerField(self):
        """Tests that a random instance has a proper CommaSeparatedIntegerField."""
        self.assertNotEquals(self.model_test.commaseparated_field, None)
        # TODO: check max_length

    def testDateField(self):
        """Tests that a random instance has a proper DateField."""
        self.assertNotEquals(self.model_test.date_field, None)

    def testDateTimeField(self):
        """Tests that a random instance has a proper DateTimeField."""
        self.assertNotEquals(self.model_test.datetime_field, None)

    def testDecimalField(self):
        """Tests that a random instance has a proper DecimalField."""
        self.assertNotEquals(self.model_test.decimal_field, None)
        # TODO: check max_digits, decimal_places

    def testEmailField(self):
        """Tests that a random instance has a proper EmailField."""
        self.assertNotEquals(self.model_test.email_field, None)

    def testFileField(self):
        """Tests that a random instance has a proper FileField."""
        self.assertNotEquals(self.model_test.file_field, None)

    def testFilePathField(self):
        """Tests that a random instance has a proper FilePathField."""
        self.assertNotEquals(self.model_test.filepath_field, None)

    def testFloatField(self):
        """Tests that a random instance has a proper FloatField."""
        self.assertNotEquals(self.model_test.float_field, None)

    @skipUnless(_isPILInstalled(), 'Python Image Library not installed')
    def testImageField(self):
        """Tests that a random instance has a proper ImageField."""
        self.assertNotEquals(self.model_test.image_field, None)

    def testIntegerField(self):
        """Tests that a random instance has a proper IntegerField."""
        self.assertNotEquals(self.model_test.integer_field, None)

    def testIPAddressField(self):
        """Tests that a random instance has a proper IPAddressField."""
        self.assertNotEquals(self.model_test.ipaddress_field, None)

    def testNullBooleanField(self):
        """Tests that a random instance has a proper NullBooleanField.
        There is nothing to test here, as null is an accepted value."""
        self.assertTrue(True)

    def testPositiveIntegerField(self):
        """Tests that a random instance has a proper PositiveIntegerField."""
        self.assertNotEquals(self.model_test.positive_field, None)

    def testPositiveSmallIntegerField(self):
        """Tests that a random instance has a proper PositiveSmallIntegerField."""
        self.assertNotEquals(self.model_test.positivesmall_field, None)

    def testSlugField(self):
        """Tests that a random instance has a proper SlugField."""
        self.assertNotEquals(self.model_test.slug_field, None)

    def testSmallIntegerField(self):
        """Tests that a random instance has a proper SmallIntegerField."""
        self.assertNotEquals(self.model_test.small_field, None)

    def testTextField(self):
        """Tests that a random instance has a proper TextField."""
        self.assertNotEquals(self.model_test.text_field, None)

    def testURLField(self):
        """Tests that a random instance has a proper URLField."""
        self.assertNotEquals(self.model_test.url_field, None)

    def testXMLField(self):
        """Tests that a random instance has a proper XMLField."""
        self.assertNotEquals(self.model_test.xml_field, None)

    # def testNotRepeatedValue(self):
    #     """Tests that two instances do not repeat the same values."""
    #     first_model  = get_or_create_random(TestingModel, id=1)
    #     second_model = get_or_create_random(TestingModel, id=2)
    #     for field in TestingModel._meta.fields:
    #         first_value  = eval('first_model.'  + field.name)
    #         second_value = eval('second_model.' + field.name)
    #         self.assertNotEquals(first_value, second_value)

