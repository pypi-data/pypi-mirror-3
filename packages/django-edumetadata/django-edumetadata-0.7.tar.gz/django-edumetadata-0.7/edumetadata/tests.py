from django.test import TestCase

from .models import Grade, GeologicTime


class edumetadataTest(TestCase):
    """
    Tests for django-edumetadata
    """
    fixtures = ['default_grades.json']

    def test_grades(self):
        self.assertEqual(Grade.objects.all().as_grade_range(), 'preschool - 13')
        self.assertEqual(Grade.objects.filter(min_age=5).as_grade_range(), 'K')
        self.assertEqual(Grade.objects.all().as_age_range(), 'all ages')
        self.assertEqual(Grade.objects.filter(max_age__lt=11).as_age_range(), '10 and under')
        self.assertEqual(Grade.objects.filter(min_age__gt=10).as_age_range(), '11 and up')
        self.assertEqual(Grade.objects.filter(min_age__gt=5, max_age__lt=15).as_age_range(), '6 - 14')
        self.assertEqual(Grade.objects.filter(min_age=5).as_age_range(), '5 - 6')
        self.assertEqual(Grade.objects.filter(min_age=0).as_age_range(), '4 and under')
        self.assertEqual(Grade.objects.filter(max_age=99).as_age_range(), '18 and up')

        self.assertEqual(Grade.objects.all().as_grade_age_range(), ('all grades', 'all ages'))
        self.assertEqual(Grade.objects.filter(min_age=5).as_grade_age_range(), ('K', '5 - 6'))
        self.assertEqual(Grade.objects.filter(max_age__lt=11).as_grade_age_range(), ('4 and under', '10 and under'))
        self.assertEqual(Grade.objects.filter(min_age__gt=10).as_grade_age_range(), ('6 and up', '11 and up'))
        self.assertEqual(Grade.objects.filter(min_age__gt=5, max_age__lt=15).as_grade_age_range(), ('1 - 8', '6 - 14'))
        self.assertEqual(Grade.objects.filter(min_age=0).as_grade_age_range(), ('preschool', '4 and under'))
        self.assertEqual(Grade.objects.filter(max_age=99).as_grade_age_range(), ('13', '18 and up'))

    def test_geologictime(self):
        self.assertEquals(GeologicTime.make_label(-1234567890), "1,235 mya")
        self.assertEquals(GeologicTime.make_label(-123456789), "123.5 mya")
        self.assertEquals(GeologicTime.make_label(-1234567), "1.23 mya")
        self.assertEquals(GeologicTime.make_label(-123456), "123,456 ya")

    def test_historicaldate(self):
        from .fields import HistoricalDate
        from datetime import date, datetime
        import sys
        assert(str(HistoricalDate(-30000))=="3 BCE")
        assert(str(HistoricalDate(-105001200))=="Dec 10500 BCE")
        assert(str(HistoricalDate(-45000406))=="6 Apr 4500 BCE")
        assert(str(HistoricalDate(30000))=="3 CE")
        assert(str(HistoricalDate(20001200))=="Dec 2000 CE")
        assert(str(HistoricalDate(16200406))=="6 Apr 1620 CE")
        assert(HistoricalDate(99999999).value==sys.maxint)
        self.assertRaises(ValueError, HistoricalDate, (999,)) # Not enough digits
        self.assertRaises(ValueError, HistoricalDate, (-999,)) # Not enough digits
        self.assertRaises(ValueError, HistoricalDate, (11331,)) # invalid month
        self.assertRaises(ValueError, HistoricalDate, (10231,)) # invalid day for month
