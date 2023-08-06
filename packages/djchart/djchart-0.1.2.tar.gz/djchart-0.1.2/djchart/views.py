from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, timedelta
from djchart.models import Chart
import sys
import json
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound

@login_required
def site_analytics(request):
    return render_to_response('djchart/site_analytics.html')

def user_registrations(request):
    DATE_FORMAT = '%d.%m'
    users = User.objects.filter(date_joined__gte=datetime.now() - timedelta(31)) \
        .only('date_joined')[:]
    regs_by_date = {}
    for user in users:
        date_joined = user.date_joined.strftime(DATE_FORMAT)
        if date_joined in regs_by_date:
            regs_by_date[date_joined] += 1
        else:
            regs_by_date[date_joined] = 1
    today = date.today()
    past_date = today - timedelta(30)
    values = []
    while past_date <= today:
        date_key = past_date.strftime(DATE_FORMAT)
        values.append([
            date_key,
            date_key in regs_by_date and regs_by_date[date_key] or 0])
        past_date += timedelta(1)
    return HttpResponse(json.dumps([values]), mimetype='text/json')

def chart_data(request, chart_pk):
    chart = get_object_or_404(Chart, pk=chart_pk)
    if chart.auth_required:
        if not hasattr(request, 'user') or not request.user.is_authenticated():
            return HttpResponseForbidden()
    def get_data_response():
        path = chart.data_provider.rsplit('.', 1)
        __import__(path[0])
        return getattr(sys.modules[path[0]], path[1])(request)
    if chart.is_data_caching_enabled():
        if not chart.is_data_cache_valid():
            response = get_data_response()
            chart.set_data_cache(response.content)
            chart.save()
            return response
        else:
            return HttpResponse(chart.data_cache, mimetype='text/json')
    else:
        if not chart.is_data_cache_empty():
            chart.set_data_cache('')
            chart.save()
        return get_data_response()

def test(request):
    return HttpResponse(
        '[[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,-219.9]]]',
        mimetype='text/json')
