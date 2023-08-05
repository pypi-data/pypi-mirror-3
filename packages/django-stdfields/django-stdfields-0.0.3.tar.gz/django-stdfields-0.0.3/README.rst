================
django-stdfields
================

Fields I wish were standard in Django. At the moment this is limited to the
``MinutesField``, ``EnumIntegerField`` and ``EnumCharField``.

Contents
========

* ``stdfields.forms.MinutesField``: use an integer to represent a duration of 
  minutes and hours
* ``stdfields.fields.EnumIntegerField``: makes working with ``choices`` a bit 
  easier
* ``stdfields.fields.EnumCharField``: the same, but for ``choices`` with a char 
  key

MinutesField
------------
Is an extension of Django's standard ``django.forms.IntegerField``.

This field will accept values for a duration in minutes in the formats 
``hh:mm`` or ``h.fraction``, similar to the way BaseCamp allows you to specify 
your time spent on a task as either ``8:30`` or ``8.5``. In the latter case only 
``8.25``, ``8.5``, ``8.50`` and ``8.75`` are considered valid inputs.

Example
^^^^^^^
Actions speak louder than words::

    # models.py
    class Task(models.Model):
        time_spent = models.IntegerField()

    # forms.py
    from stdfields.forms import MinutesField
    
    from models import Task
    
    class TaskForm(forms.ModelForm):
        time_spent = MinutesField(label='How long did it take?')
        
        class Meta:
            model = Task
            
You can use the ``minutes`` template filter from ``stdfieldstags`` to render
such a field in the format ``8:30``::

    {% load stdfieldstags %}
    It took me {{ task.time_spent|minutes }} to complete this task.


Enumeration
-----------
I always end up with ugly code when using Django's ``choices`` argument for 
fields. With the ``stdfields.models.Enumeration`` class, I've got a handy base 
class that allows me to keep things tidy::

    # models.py
    class Color(Enumeration):
        RED = 'R'
        GREEN = 'G'
        BLUE = 'B'
    
        @classmethod
        def all(cls):
            return [
                (cls.RED, _(u'Red')),
                (cls.GREEN, _(u'Green')),
                (cls.BLUE, _(u'Blue'))
            ]
            
    class Pencil(models.Model):
        color = models.CharField(choices=Color.all(), max_length=Color.max_length())
        
    # views.py
    def red_pencils(request):
        pencils = Pencil.objects.filter(color=Color.RED)
        ...
        # Prints 'Showing the Red pencils'
        logging.info('Showing the %s pencils' % (Color.as_display(Color.RED)))


EnumCharField and EnumIntegerField
----------------------------------
And now we can make working with an ``Enumeration`` easier with the 
``EnumCharField`` and ``EnumIntegerField`` models fields::

    # models.py
    class Color(Enumeration):
        # same as above
        
    class Pencil(models.Model):
        color = models.EnumCharField(enum=Color, max_length=Color.max_length())
        
This example is basically the same as the above since ``EnumCharField`` is a 
subclass of the regular Django ``CharField``. By using the ``enum`` keyword 
argument of the enum field, the choices will be automatically updated when you
update the enumeration object. And since you're using the provided 
``max_length`` method of ``Enumeration``, the ``max_length`` will be updated
when needed. Just like in the previous example. The enum fields simply offer 
some more clarity when reading the code.

``EnumIntegerField`` works exactly the same, but for enumerations with integer
keys. Both fields can be used with South.
