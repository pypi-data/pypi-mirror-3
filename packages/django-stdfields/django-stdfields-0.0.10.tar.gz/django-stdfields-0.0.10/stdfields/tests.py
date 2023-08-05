# -*- coding: utf-8 -*-
"""
Test cases for forms.MinutesField, forms.MinutesWidget, fields.MinutesField,
fields.EnumIntegerField and fields.EnumCharField.
"""
from django.test import TestCase
from django.forms import ValidationError, ModelForm
from django.db import models

from stdfields.models import Enumeration, Enum, EnumValue
from stdfields.fields import MinutesField, EnumIntegerField, EnumCharField
from stdfields.forms import MinutesField as MinutesFormField
from stdfields.widgets import MinutesWidget

# -- --------------------------------------------------------------------------
# -- MinutesField + MinutesWidget test

class Task(models.Model):
    minutes = MinutesField()


class TaskForm(ModelForm):

    class Meta:
        model = Task


class MinutesFieldTest(TestCase):

    def test_minutes_field(self):
        t = Task(minutes=121)
        self.assertEqual(121, t.minutes)
        t.save()
        self.assertEqual(121, t.minutes)

    def test_form_field(self):
        form = TaskForm()
        self.assertEqual(MinutesFormField, type(form.fields['minutes']))


class MinutesFormFieldTest(TestCase):

    def test_minutes_field(self):
        f = MinutesFormField()
        self.assertEqual(120, f.clean(2))
        self.assertEqual(121, f.clean('2:01'))
        self.assertEqual(121, f.clean('2:1'))
        self.assertEqual(120, f.clean('2'))
        self.assertEqual(150, f.clean('2.5'))
        self.assertEqual(150, f.clean('2,5'))
        self.assertEqual(150, f.clean('2.50'))
        self.assertEqual(150, f.clean('2.50.120'))
        self.assertEqual(135, f.clean('2.25'))
        self.assertEqual(165, f.clean('2.75'))
        minutes = 480
        for i in range(60):
            self.assertEqual(minutes + i, f.clean('8:%d' % (i)))

    def test_minutes_field_invalid(self):
        f = MinutesFormField()
        self._should_raise_validation_error(f, '2:60')
        self._should_raise_validation_error(f, 'x:60')
        self._should_raise_validation_error(f, 'x:y')
        self._should_raise_validation_error(f, '2;30')
        self._should_raise_validation_error(f, '2;30')

    def _should_raise_validation_error(self, f, value):
        try:
            f.clean(value)
            self.fail('%s should raise a ValidationError' % (value))
        except ValidationError, e:
            pass


class MinutesWidgetTest(TestCase):

    def test_minutes_widget(self):
        w = MinutesWidget()
        tpl = '<input type="text" name="hi" value="%s" />'
        self.assertEqual(w.render('hi', '121'), tpl % '2:01')
        self.assertEqual(w.render('hi', '2:1'), tpl % '2:1')
        self.assertEqual(w.render('hi', '2:60'), tpl % '2:60')
        self.assertEqual(w.render('hi', '493'), tpl % '8:13')

# -- --------------------------------------------------------------------------
# -- Enum tests

class SimpleExampleIntegerEnum(Enum):
    FIRST = EnumValue(1, 'First')
    SECOND = EnumValue(2, 'Second')
    THIRD = EnumValue(3, 'Third')

class ExtendedIntegerEnum(SimpleExampleIntegerEnum):
    FOURTH = EnumValue(4, 'Fourth')
    FIFTH = EnumValue(5, 'Fifth')
    SIXTH = EnumValue(6, 'Sixth')
    SEVENTH = EnumValue(7, 'Seventh')

class EnumTest(TestCase):

    def test_order(self):
        values = SimpleExampleIntegerEnum.all()
        self.assertEqual(SimpleExampleIntegerEnum.FIRST, values[0][0])
        self.assertEqual(SimpleExampleIntegerEnum.SECOND, values[1][0])
        self.assertEqual(SimpleExampleIntegerEnum.THIRD, values[2][0])

    def test_order_extended(self):
        values = ExtendedIntegerEnum.all()
        self.assertEqual(ExtendedIntegerEnum.FIRST, values[0][0])
        self.assertEqual(ExtendedIntegerEnum.SECOND, values[1][0])
        self.assertEqual(ExtendedIntegerEnum.THIRD, values[2][0])
        self.assertEqual(ExtendedIntegerEnum.FOURTH, values[3][0])
        self.assertEqual(ExtendedIntegerEnum.FIFTH, values[4][0])
        self.assertEqual(ExtendedIntegerEnum.SIXTH, values[5][0])
        self.assertEqual(ExtendedIntegerEnum.SEVENTH, values[6][0])

    def test_display(self):
        self.assertEqual(SimpleExampleIntegerEnum.THIRD_display, 'Third')
        self.assertEqual(ExtendedIntegerEnum.THIRD_display, 'Third')
        self.assertEqual(ExtendedIntegerEnum.SIXTH_display, 'Sixth')


# -- --------------------------------------------------------------------------
# -- EnumIntegerField tests

class ExampleIntegerEnum(Enumeration):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    enumeration = [
        (FIRST, 'First'),
        (SECOND, 'Second'),
        (THIRD, 'Third'),
    ]


class EnumIntegerModel(models.Model):
    c = EnumIntegerField(enum=ExampleIntegerEnum)


class EnumIntegerFieldTest(TestCase):
    enum = ExampleIntegerEnum
    model = EnumIntegerModel

    def test_enum_integer_field(self):
        f = EnumIntegerField(enum=self.enum,
                            default=self.enum.FIRST, blank=False)
        self.assertEqual(self.enum.all(), f.formfield().choices)
        f = EnumIntegerField(enum=self.enum)
        expected = [('', '---------')] + self.enum.all()
        self.assertEqual(expected, f.formfield().choices)

    def test_display(self):
        first = self.enum.FIRST
        label = self.enum.as_display(first)
        self.assertEqual(label, self.model(c=first).get_c_display())
        self.assertEqual(5, self.model(c=5).get_c_display())
        self.assertTrue(self.model(c=None).get_c_display() is None)
        self.assertEqual('', self.model(c='').get_c_display())


class PureIntegerEnum(Enum):
    FIRST = EnumValue(1, 'First')
    SECOND = EnumValue(2, 'Second')
    THIRD = EnumValue(3, 'Third')


class PureEnumIntegerModel(models.Model):
    c = EnumIntegerField(enum=PureIntegerEnum)


PureEnumIntegerFieldTest = EnumIntegerFieldTest
PureEnumIntegerFieldTest.enum = PureIntegerEnum
PureEnumIntegerFieldTest.model = PureEnumIntegerModel

# -- --------------------------------------------------------------------------
# -- EnumCharField tests

class ExampleCharEnum(Enumeration):
    FIRST = 'A'
    SECOND = 'Boo'
    THIRD = 'Circus'
    enumeration = [
        (FIRST, 'First'),
        (SECOND, 'Second'),
        (THIRD, 'Third'),
    ]


class EnumCharModel(models.Model):
    c = EnumCharField(enum=ExampleCharEnum,
                    max_length=ExampleCharEnum.max_length())


class EnumCharFieldTest(TestCase):
    
    def __init__(self, *args, **kwargs):
        super(EnumCharFieldTest, self).__init__(*args, **kwargs)
        self.enum_cls = ExampleCharEnum
        self.model_cls = EnumCharModel
        # 'Circus' is the longest key at 6 characters
        self.max_length = 6

    def test_enum_char_field(self):
        enum = self.enum_cls
        f = EnumCharField(enum=enum, default=enum.FIRST,
                        blank=False, max_length=enum.max_length())
        self.assertEqual(self.max_length, f.max_length)
        self.assertEqual(enum.all(), f.formfield().choices)
        f = EnumCharField(enum=enum)
        expected = [('', '---------')] + enum.all()
        self.assertEqual(expected, f.formfield().choices)

    def test_display(self):
        enum = self.enum_cls
        model = self.model_cls
        first = enum.FIRST
        label = enum.as_display(first)
        self.assertEqual(label, model(c=first).get_c_display())
        self.assertEqual('E', model(c='E').get_c_display())
        self.assertTrue(model(c=None).get_c_display() is None)
        self.assertEqual('', model(c='').get_c_display())


class PureCharEnum(Enum):
    FIRST = EnumValue('A', 'First')
    SECOND = EnumValue('Boo', 'Second')
    THIRD = EnumValue('Circus', 'Third')


class PureEnumCharModel(models.Model):
    c = EnumCharField(enum=PureCharEnum,
                    max_length=PureCharEnum.max_length())


class PureEnumCharFieldTest(EnumCharFieldTest):

    def __init__(self, *args, **kwargs):
        super(PureEnumCharFieldTest, self).__init__(*args, **kwargs)
        self.enum_cls = PureCharEnum
        self.model_cls = PureEnumCharModel


class PureCharEnumExtension(PureCharEnum):
    FOURTH = EnumValue('FICTIONAL', 'Acme Inc')
    FIFTH = EnumValue('Wtf?', 'Stop the train!')


class PureEnumCharExtensionModel(models.Model):
    c = EnumCharField(enum=PureCharEnumExtension,
                    max_length=PureCharEnumExtension.max_length())


class PureEnumCharExtensionFieldTest(EnumCharFieldTest):

    def __init__(self, *args, **kwargs):
        super(PureEnumCharExtensionFieldTest, self).__init__(*args, **kwargs)
        self.enum_cls = PureCharEnumExtension
        self.model_cls = PureEnumCharExtensionModel
        self.max_length = 9

    def test_display_extra_values(self):
        enum = self.enum_cls
        model = self.model_cls
        first = enum.FIFTH
        label = 'Stop the train!'
        self.assertEqual(label, enum.as_display(first))
        self.assertEqual(label, model(c=first).get_c_display())
        self.assertEqual('E', model(c='E').get_c_display())
        self.assertTrue(model(c=None).get_c_display() is None)
        self.assertEqual('', model(c='').get_c_display())
