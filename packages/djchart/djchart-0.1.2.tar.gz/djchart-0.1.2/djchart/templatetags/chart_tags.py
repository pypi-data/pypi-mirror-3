import sys
from django.core.urlresolvers import reverse
from django import template
from django.http import HttpRequest, HttpResponseForbidden
from djchart.models import Chart
from djchart.views import chart_data

register = template.Library()

def insert_chart_internals(pk, el_id, ajax=False):
	try:
		chart = Chart.objects.get(pk=pk)
	except:
		return '<!-- Error: requested chart not found! -->'
	def script(script_text):
		return '<script type="text/javascript" language="JavaScript">//<![CDATA[\n%s\n//]]></script>' \
			% script_text
	if ajax:
		return script('ajaxChart("%(id)s", "%(path)s", %(options)s);'
			% {
				'id': unicode(el_id),
				'path': reverse('chart_data', kwargs={'chart_pk': pk}),
				'options': any(chart.options) and chart.options or 'null',})
	else:
		data_response = chart_data(HttpRequest(), pk)
		if isinstance(data_response, HttpResponseForbidden):
			return '<!-- Error: authorisation required -->'
		return script('$.jqplot("%(id)s", %(data)s, %(options)s);'
			% {
				'id': unicode(el_id),
				'data': data_response.content,
				'options': any(chart.options) and chart.options or 'null',})

@register.simple_tag
def insert_chart(pk, el_id, ajax=False):
    return insert_chart_internals(pk, el_id, ajax)
