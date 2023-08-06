from djchart.templatetags.chart_tags import insert_chart_internals

def charts(request):
	return {
		'insert_chart': insert_chart_internals,
	}
