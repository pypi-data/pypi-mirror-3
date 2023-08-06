from django.db import models
from django.db.models.query import QuerySet
from django.template.defaultfilters import slugify

from .fields import HistoricalDateField
from .settings import ERA_TYPE_CHOICES

from categories.base import CategoryBase

try:
    from django.db.models import BigIntegerField
except ImportError:
    from .fields import BigIntegerField


class GradeManager(models.Manager):
    """
    Adds grade-specific methods for querysets
    """
    class GradeQuerySet(QuerySet):
        """
        Custom Queryset to add special formatting options to results
        """
        def as_struct(self):
            """
            Convert the query set into a structure for flexible formatting

            Returns a dict:
                age_lower    The name of the lowest age in the QuerySet
                age_upper    The name of the highest age in the QuerySet
                age_plural   Boolean flag indicating more than 1 age
                grade_lower  The name of the lowest grade in the QuerySet
                grade_upper  The name of the highest grade in the QuerySet
                grade_plural Boolean flag indicating more than 1 grade
                lower_bounds Boolean flag indicating there is no lower boundary
                               False basically means "and under"
                upper_bounds Boolean flag indicate there is no upper boundary
                               False basically means "and up"
            Returns None if there is an empty QuerySet
            """
            grades_ages = list(self)
            result = {
                'age_lower': None,
                'age_upper': None,
                'age_plural': False,
                'grade_lower': None,
                'grade_upper': None,
                'grade_plural': False,
                'lower_bounds': False,
                'upper_bounds': False
            }
            if len(grades_ages) == 0:
                return None
            result['age_lower'] = str(grades_ages[0].min_age)
            result['age_upper'] = str(grades_ages[-1].max_age)
            result['age_plural'] = grades_ages[0].min_age != grades_ages[-1].max_age
            result['grade_lower'] = grades_ages[0].name
            result['grade_upper'] = grades_ages[-1].name
            result['grade_plural'] = len(grades_ages) > 1
            result['upper_bounds'] = grades_ages[-1].max_age != 99
            result['lower_bounds'] = grades_ages[0].min_age != 0

            return result

        def get_range_string(self, struct, grade_or_age):
            """
            Given a grade/age struct, return either the grade or age string
            as a range

            One of:
            A
            A - B
            A and up
            B and under
            all
            """
            if struct is None:
                return ''
            if struct['upper_bounds'] and struct['lower_bounds']:
                if not struct['%s_plural' % grade_or_age]:
                    return struct['%s_lower' % grade_or_age]  # A single, bounded value
                return "%s - %s" % (struct['%s_lower' % grade_or_age],
                                    struct['%s_upper' % grade_or_age])  # bounded values
            elif struct['upper_bounds'] and not struct['lower_bounds']:
                if struct['%s_plural' % grade_or_age]:
                    return "%s and under" % struct['%s_upper' % grade_or_age]  # upper-bounded value
                else:
                    return struct['%s_upper' % grade_or_age]
            elif not struct['upper_bounds'] and struct['lower_bounds']:
                if struct['%s_plural' % grade_or_age]:
                    return "%s and up" % struct['%s_lower' % grade_or_age]  # lower-bounded value
                else:
                    return struct['%s_lower' % grade_or_age]
            elif not struct['upper_bounds'] and not struct['lower_bounds']:
                return "all %ss" % grade_or_age

        def as_grade_age_range(self):
            """
            Returns the query set as a tuple for grades, ages
            """
            grades_ages = self.as_struct()
            return (
                self.get_range_string(grades_ages, 'grade'),
                self.get_range_string(grades_ages, 'age'),
            )

        def as_grade_range(self):
            """
            Converts the queryset to a string "x - y"
            """
            grades = list(self.values_list('name', flat=True))
            if len(grades) == 0:
                return ''
            elif len(grades) == 1:
                return str(grades[0])
            return "%s - %s" % (grades[0], grades[-1])

        def as_age_range(self):
            """
            Converts the queryset to a string "x.min_age - y.max_age"
            """
            ages = list(self.values_list('min_age', 'max_age'))
            post_string = ""
            age_list = []
            if len(ages) == 0:
                return ''
            if ages[0][0] == 0:  # No lower bound
                post_string = " and under"
            else:
                age_list.append(str(ages[0][0]))
            if ages[-1][1] == 99:  # No upper bound
                if post_string:
                    return "all ages"
                else:
                    post_string = " and up"
            else:
                age_list.append(str(ages[-1][1]))
            return "%s%s" % (" - ".join(age_list), post_string)

    def get_query_set(self):
        return self.GradeQuerySet(self.model)


class Grade(models.Model):
    """
    Education grade levels
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    min_age = models.IntegerField(
        default=0,
        help_text="The minimum age of a student in this grade. "
                  "Set to 0 to signify 'and under'")
    max_age = models.IntegerField(
        default=99,
        help_text="The maximum age of a student in this grade. "
                  "Set to 99 to signify 'and over'")
    order = models.IntegerField(default=0)

    objects = GradeManager()

    @property
    def ages(self):
        """
        Pretty print the ages
        """
        post_string = ""
        age_list = []
        if self.min_age == 0:  # No lower bound
            post_string = " and under"
        else:
            age_list.append(str(self.min_age))
        if self.max_age == 99:  # No upper bound
            if post_string:
                return "all ages"
            else:
                post_string = " and up"
        else:
            age_list.append(str(self.max_age))
        return "%s%s" % (" - ".join(age_list), post_string)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Make sure the slug is set.
        """
        if not self.slug:
            self.slug = slugify(self.name)[:50]
        super(Grade, self).save(*args, **kwargs)

    class Meta:
        ordering = ('order', 'name')


class Subject(CategoryBase):
    """
    Education subjects and their disciplines
    """
    more_info_url = models.CharField(
        blank=True, null=True,
        max_length=256,
        help_text="A URL in which to find more information.")


class EducationCategory(CategoryBase):
    """
    Education-specific categories
    """
    pass


class AlternateType(CategoryBase):
    """
    Alternate Content Type specifications
    """
    class Meta(CategoryBase.Meta):
        verbose_name = "secondary content type"
        verbose_name_plural = "secondary content types"


class GeologicTime(CategoryBase):
    """
    Hierarchical collection of Eons, Era, Period, Epoch, Age
    """
    start_label = models.CharField(max_length=255, editable=False, blank=True)
    end_label = models.CharField(max_length=255, editable=False, blank=True)
    start = BigIntegerField()
    end = BigIntegerField()

    @staticmethod
    def make_label(years_ago):
        """
        Convert a number of years ago into a label.

        E.g: -1000000 -> 1 Mya
        """
        import locale
        locale.setlocale(locale.LC_ALL, '')
        if years_ago <= -1000000:
            value = round(years_ago / -1000000.0, 2)
            output = locale.format_string("%0.4g mya", value, grouping=True)
        elif years_ago == 0:
            output = "present"
        else:
            output = locale.format("%d", years_ago * -1, grouping=True) + " ya"
        return output

    def save(self, *args, **kwargs):
        """
        Update labels
        """
        self.start_label = self.make_label(self.start)
        self.end_label = self.make_label(self.end)
        super(GeologicTime, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.name, self.start_label, self.end_label)

    class MPTTMeta:
        order_insertion_by = ('start',)


class HistoricalEra(models.Model):
    """
    Historical Eras for educational content
    """
    name = models.CharField(max_length=100)
    era_type = models.IntegerField(choices=ERA_TYPE_CHOICES)
    start = HistoricalDateField()
    end = HistoricalDateField(blank=True, null=True)

    def __unicode__(self):
        from .fields import HistoricalDate
        if not self.end:
            return "%s (%s - present)" % (self.name, HistoricalDate(self.start))
        return "%s (%s - %s)" % (self.name, HistoricalDate(self.start), HistoricalDate(self.end))
