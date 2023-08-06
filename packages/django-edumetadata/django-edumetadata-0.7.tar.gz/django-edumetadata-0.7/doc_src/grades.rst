===============
Grades Metadata
===============

Goals
=====

* Allow for an age range to accompany each level.
* Have a specific order
* Be able to convert a range of grades (and ages) into a human-readable string (e.g. '4-6', '6 and under')
* Age ranges must allow for no lower and no upper boundaries

Introduction
============

A grade is a level of study or achievement within a subject area or educational institution. Grade metadata is meant to indicate that the related object is appropriate for the related grade levels.

Model Reference
===============

.. py:class:: Grade

   .. py:attribute:: name
   
      **Required** ``CharField(100)``
      
      The display name for the grade level. For example ``preschool``, or ``1``.
   
   .. py:attribute:: slug
   
      **Required** ``SlugField``
      
      A URL-friendly version of the name.
   
   .. py:attribute:: min_age
   
      **Required** ``IntegerField`` *default:* ``0``
      
      A minimum age for this grade level. ``0`` signifies there is no lower boundary or the grade's ``max_age`` 'and under.' A ``min_age`` of ``0`` and a ``max_age`` of ``99`` indicates there is no age limit.
   
   .. py:attribute:: max_mage
   
      **Required** ``IntegerField`` *default:* ``99``
      
      The maximum age allowed for this grade level. ``99`` signifies there is no upper boundary or the grade's ``min_age`` 'and up.' A ``min_age`` of ``0`` and a ``max_age`` of ``99`` indicates there is no age limit.
      
   .. py:attribute:: order
   
      **Required** ``IntegerField`` *default:* ``0``
      
      The order in which this grade should appear in relation to the other grades.
   
   .. py:attribute:: ages
   
      A ``property`` to pretty-print the ages. Returns ``x - y`` where ``x`` is the ``min_age`` and ``y`` is the ``max_age``. If the ``min_age`` is ``0``, it returns ``y and under``. If ``max_age`` is ``99``, it returns ``x and up``. If ``min_age`` is ``0`` and ``max_age`` is ``99`` it returns ``all ages``.


Manager Reference
=================

The grade manager has some special functions to provide better output for ranges. Any query on the :py:class:`Grade` model returns a :py:class:`GradeQuerySet`, which is a subclass of Django's :py:class:`QuerySet` with a few new methods.

.. py:class:: GradeQuerySet

   .. py:method:: as_grade_age_range
      :returns: Tuple
      
      Returns strings containing the range of grade names and ages.
      
      Instead of returning a :py:class:`QuerySet` with each grade level, it returns a ``tuple`` of ``string``\ s. The first element is the grade name's range in the format ``x - y``. The second element is the grade ages output in the same method as :py:attribute:`Grade.ages`.