# Some useful views related to public holidays.

import datetime
import simplejson as json

from django.shortcuts import render_to_response
from django.db.models import Q
from django.http import HttpResponse

from models import PublicHoliday

def holidays(request, country, year, province=None):
    start = datetime.date(int(year), 1, 1)
    finish = datetime.date(int(year), 12, 31)
    country = country.upper()
    
    holidays = PublicHoliday.objects.filter(country=country, 
        date__gte=start, date__lte=finish)
    
    if province:
        holidays = holidays.filter(Q(provinces__contains=province)|Q(provinces=None))
    
    format = request.GET.get('format', 'html')
    
    # if format == "json":
    #     return HttpResponse(json.dumps(holidays.values('country', 'provinces', 'name', 'date')))
        
    return render_to_response('public_holidays/year.%s' % format, {
        'holidays': holidays,
        'country': country,
        'year': year,
        'province': province
    })