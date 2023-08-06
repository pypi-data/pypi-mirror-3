from django.db import models
from django.utils.translation import ugettext_lazy, ugettext as _

import django_countries
import jsonfield.fields

class PublicHolidayManager(models.Manager):
    def on(self, date, country, province=None):
        """
        If no province is provided, any holiday that falls on that day
        for that country will return True
        """
        # TODO: handle country names as well as codes.
        qs = self.get_query_set().filter(date=date, country=country)
        
        if province:
            qs = qs.filter(models.Q(provinces=None) | models.Q(provinces__contains=province))
        
        return qs.exists()
    
    
class PublicHoliday(models.Model):
    """
    A PublicHoliday is an object that can be associated with a country, and
    zero or more provinces. The semantic meaning of no listed provinces is
    that the PublicHoliday is nationwide.
    
    The provinces list should be CSV list of provinces from the django
    localflavor module.
    
    This is a seperate app, that relies on django-countries, with my
    province patches applied, and django-jsonfield.
    """
    
    #: Every PublicHoliday must have a name.
    name = models.CharField(max_length=128)
    #: PublicHolidays are single-day events, and do not automatically repeat.
    date = models.DateField()
    #: Each PublicHoliday can only apply to one country.
    country = django_countries.CountryField()
    #: Each PublicHoliday can apply to all, or a subset of provinces in
    #: a country.
    provinces = jsonfield.fields.JSONField(null=True, blank=True,
        help_text=_(u'No selected provinces means that all provinces are affected.'))
    
    objects = PublicHolidayManager()
    
    class Meta:
        app_label = 'public_holidays'
        verbose_name = u'public holiday'
        verbose_name_plural = u'public holidays'
        ordering = ('date', 'country')
        unique_together = (
            ('name', 'date', 'country'),
        )
    
    def __unicode__(self):
        return "%s (%s) [%s]" % (self.name, self.date.year, self.country)


def public_holiday_on(date, country, province):
    return PublicHoliday.objects.on(date, country, province)