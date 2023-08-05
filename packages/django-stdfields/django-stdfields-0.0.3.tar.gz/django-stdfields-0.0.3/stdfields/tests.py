# -*- coding: utf-8 -*-
"""
Test cases for forms.MinutesField, forms.MinutesWidget, fields.MinutesField,
fields.EnumIntegerField and fields.EnumCharField.
"""
from django.test import TestCase
from django.forms import ValidationError, ModelForm
from django.db import models

from stdfields.models import Enumeration
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
# -- EnumIntegerField tests

class ExampleIntegerEnum(Enumeration):
    FIRST = 1
    SECOND = 2
    THIRD = 3

    @classmethod
    def all(cls):
        return [
            (cls.FIRST, 'First'),
            (cls.SECOND, 'Second'),
            (cls.THIRD, 'Third'),
        ]


class EnumIntegerModel(models.Model):
    c = EnumIntegerField(enum=ExampleIntegerEnum)


class EnumIntegerFieldTest(TestCase):

    def test_enum_integer_field(self):
        f = EnumIntegerField(enum=ExampleIntegerEnum,
                            default=ExampleIntegerEnum.FIRST, blank=False)
        self.assertEqual(ExampleIntegerEnum.all(), f.formfield().choices)
        f = EnumIntegerField(enum=ExampleIntegerEnum)
        expected = [('', '---------')] + ExampleIntegerEnum.all()
        self.assertEqual(expected, f.formfield().choices)

    def test_display(self):
        first = ExampleIntegerEnum.FIRST
        label = ExampleIntegerEnum.as_display(first)
        self.assertEqual(label, EnumIntegerModel(c=first).get_c_display())
        self.assertEqual(5, EnumIntegerModel(c=5).get_c_display())
        self.assertTrue(EnumIntegerModel(c=None).get_c_display() is None)
        self.assertEqual('', EnumIntegerModel(c='').get_c_display())


# -- --------------------------------------------------------------------------
# -- EnumCharField tests

class ExampleCharEnum(Enumeration):
    FIRST = 'A'
    SECOND = 'Boo'
    THIRD = 'Circus'

    @classmethod
    def all(cls):
        return [
            (cls.FIRST, 'First'),
            (cls.SECOND, 'Second'),
            (cls.THIRD, 'Third'),
        ]


class EnumCharModel(models.Model):
    c = EnumCharField(enum=ExampleCharEnum,
                    max_length=ExampleCharEnum.max_length())


class EnumCharFieldTest(TestCase):

    def test_enum_char_field(self):
        f = EnumCharField(enum=ExampleCharEnum, default=ExampleCharEnum.FIRST,
                        blank=False, max_length=ExampleCharEnum.max_length())
        # 'Circus' is the longest key at 6 characters
        self.assertEqual(6, f.max_length)
        self.assertEqual(ExampleCharEnum.all(), f.formfield().choices)
        f = EnumCharField(enum=ExampleCharEnum)
        expected = [('', '---------')] + ExampleCharEnum.all()
        self.assertEqual(expected, f.formfield().choices)

    def test_display(self):
        first = ExampleCharEnum.FIRST
        label = ExampleCharEnum.as_display(first)
        self.assertEqual(label, EnumCharModel(c=first).get_c_display())
        self.assertEqual('E', EnumCharModel(c='E').get_c_display())
        self.assertTrue(EnumCharModel(c=None).get_c_display() is None)
        self.assertEqual('', EnumCharModel(c='').get_c_display())
