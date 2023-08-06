import sys
from datetime import date, datetime

from django.db import models
from django.conf import settings
from django import forms
from django.core import exceptions


class BigIntegerField(models.IntegerField):
    """
    An 8-byte integer field for Django versions < 1.2
    """
    def db_type(self):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigint"
        elif settings.DATABASE_ENGINE == 'sqlite3':
            return 'integer'
        else:
            raise NotImplementedError

    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                "This value must be a long integer.")


def get_month_choices():
    """
    Get the choices for months using the locale
    """
    import locale
    locale.setlocale(locale.LC_ALL, '')
    output = [('00', '------')]
    for i in range(1, 13):
        output.append(("%02d" % i,
            locale.nl_langinfo(getattr(locale, 'ABMON_%s' % i)))
        )
    return output


def get_day_choices():
    """
    Return the choices for days
    """
    output = [('00', '------')]
    for i in range(1, 32):
        output.append(("%02d" % i, str(i)))
    return output


class HistoricalDate(object):
    """
    A field that stores a historical date as an integer with different resolutions

    The field format is +/-YYYYYYYYMMDD

    Parsed as last 2 digits are the day, with 00 meaning not specified
    second-to-last 2 digits are month, with 00 meaning not specified
    remaining digits are year.

    Maximum year in the past is 214748 BC

    Examples:
    10000 = 1AD
    -10000 = 1BC
    0 = Undefined
    99999999 = "the present"
    19631122 = Nov 22, 1963
    -45611200 = Dec 4561BC
    """
    def __init__(self, value=None):
        if value and not isinstance(value, (int, date, datetime)):
            raise ValueError("HistoricalDate must be an int, date or datetime.")
        if value:
            if isinstance(value, (date, datetime)):
                self.from_date(value)
                return
            elif abs(value) < 10000:
                raise ValueError("HistoricalDate must have at least 5 digits.")
            elif value == 99999999:
                self.value = sys.maxint
                self.year = sys.maxint
                self.month = sys.maxint
                self.day = sys.maxint
                return
            numstr = str(value)
            day = int(numstr[-2:])
            month = int(numstr[-4:-2])
            year = int(numstr[:-4])
            if month < 1:
                month = None
            if day < 1:
                day = None
        else:
            year = month = day = None
        self.value = value
        self.year = year
        self.month = month
        self.day = day
        self.validate_month()

    def validate_month(self):
        if self.month is not None and (self.month < 1 or self.month > 12):
            raise ValueError("Invalid month in value. %s is not between 00 and 12" % self.month)

    def validate_day(self):
        if self.month is None and self.day is not None:
            raise ValueError("Day specified without month.")
        if self.day is not None and (self.day < 1):
            raise ValueError("Day less than 01")
        if self.day is not None:
            if self.year < 1:
                date(2012, self.month, self.day)  # Use a leap year for that possibility
            else:
                self.to_date()

    def to_date(self):
        if self.value == sys.maxint:
            return date.today()
        return date(self.year, self.month, self.day)

    def from_date(self, value):
        """
        Populate the values from a date.
        """
        self.year = value.year
        self.month = value.month
        self.day = value.day
        self.value = (self.year * 10000) + (self.month * 100) + self.day

    def __repr__(self):
        return "HistoricalDate(%r)" % self.value

    def __str__(self):
        import locale
        locale.setlocale(locale.LC_ALL, '')
        output = []
        if self.day is not None:
            output.append(str(self.day))
        if self.month is not None:
            output.append(locale.nl_langinfo(getattr(locale, 'ABMON_%s' % self.month)))
        output.append(str(abs(self.year)))
        if self.year < 0:
            output.append('BCE')
        else:
            output.append('CE')
        return " ".join(output)

    def __int__(self):
        return self.value

    def __cmp__(self, other):
        return cmp(self.value, int(other))


class HistoricalDateWidget(forms.MultiWidget):
    """
    A widget for a Historical Date field. Includes 3 text entry widgets and
    optional "to present" checkbox
    """
    def __init__(self, attrs=None):
        if attrs:
            new_attrs = attrs.copy()
        else:
            new_attrs = {'class': 'vDateField'}
        year_attrs = new_attrs.copy()
        year_attrs['size'] = "10"
        widgets = (forms.TextInput(attrs=year_attrs),
                   forms.Select(attrs=new_attrs, choices=(('-', 'BCE'), ('+', 'CE'))),
                   forms.Select(attrs=new_attrs, choices=get_month_choices()),
                   forms.Select(attrs=new_attrs, choices=get_day_choices()))
        return super(HistoricalDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            hdate = HistoricalDate(value)
            if hdate.year < 0:
                era = '-'
            else:
                era = '+'
            return [abs(hdate.year), era,
                    "%02d" % (hdate.month or 0), "%02d" % (hdate.day or 0)]
        return ['', '+', '00', '00']


class HistoricalDateFormField(forms.MultiValueField):
    widget = HistoricalDateWidget

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = HistoricalDateWidget
        fields = (
            forms.IntegerField(min_value=1),
            forms.ChoiceField(choices=(('-', 'BCE'), ('+', 'CE'))),
            forms.ChoiceField(choices=get_month_choices()),
            forms.ChoiceField(choices=get_day_choices())
        )
        super(HistoricalDateFormField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Convert the value list into an integer
        """
        if data_list[0] is None:
            return None
        out = int("".join([data_list[1], str(data_list[0]), data_list[2], data_list[3]]))
        return out

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': self.verbose_name,
                    'help_text': self.help_text}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return HistoricalDateWidget(**defaults)


class HistoricalDateField(models.IntegerField):
    """
    A subclass of integer that stores a HistoricalDate value.
    """
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "IntegerField"

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': HistoricalDateFormField}
        defaults.update(kwargs)
        return super(HistoricalDateField, self).formfield(**defaults)

    def get_db_prep_value(self, value, *args, **kwargs):
        if isinstance(value, basestring):
            return int(value)
        elif isinstance(value, int):
            return value
        elif isinstance(value, list):
            return int("".join(value))
