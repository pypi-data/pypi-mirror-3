from django.contrib import admin

from categories.base import CategoryBaseAdmin


from .fields import HistoricalDate
from .models import (Grade, Subject, EducationCategory, AlternateType,
                     GeologicTime, HistoricalEra)
from .settings import (ENABLE_GRADES, ENABLE_SUBJECTS, ENABLE_GEOLOGICTIME,
                        ENABLE_ALTTYPES, ENABLE_EDUCATEGORIES,
                        ENABLE_HISTORICALERAS)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'ages')
    prepopulated_fields = {'slug': ('name',)}

if ENABLE_GRADES:
    admin.site.register(Grade, GradeAdmin)


class SubjectAdmin(CategoryBaseAdmin):
    pass

if ENABLE_SUBJECTS:
    admin.site.register(Subject, SubjectAdmin)


class EducationCategoryAdmin(CategoryBaseAdmin):
    pass

if ENABLE_EDUCATEGORIES:
    admin.site.register(EducationCategory, EducationCategoryAdmin)


class AlternateTypeAdmin(CategoryBaseAdmin):
    pass

if ENABLE_ALTTYPES:
    admin.site.register(AlternateType, AlternateTypeAdmin)


class GeologicTimeAdmin(CategoryBaseAdmin):
    list_display = ('__unicode__',)

if ENABLE_GEOLOGICTIME:
    admin.site.register(GeologicTime, GeologicTimeAdmin)


class HistoricalEraAdmin(admin.ModelAdmin):
    list_display = ('name', 'era_type', 'start_year', 'end_year',)

    def start_year(self, obj):
        return HistoricalDate(obj.start).__str__()

    def end_year(self, obj):
        if obj.end:
            return HistoricalDate(obj.end).__str__()
        else:
            return ''

if ENABLE_HISTORICALERAS:
    admin.site.register(HistoricalEra, HistoricalEraAdmin)
