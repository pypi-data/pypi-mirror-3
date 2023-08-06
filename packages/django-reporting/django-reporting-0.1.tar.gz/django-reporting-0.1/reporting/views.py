from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
import reporting
from datetime import date
import csv

def report_list(request):
    reports = reporting.all_reports_names()
    return render_to_response('reporting/list.html', {'reports': reports}, 
                              context_instance=RequestContext(request))

def view_report(request, slug):
    for_csv = ''
    count_params = 0
    for key,value in request.REQUEST.iteritems():
        if count_params == 0:
            for_csv = key + '=' + value
        else:
            for_csv = for_csv + '&' + key + '=' + value
        count_params = count_params + 1
    report = reporting.get_report(slug)(request)
    if report.show_details:
        headers = report.get_details_headers()
    else:
        headers = report.get_headers()
    cant_of_group = len(headers) - len(report.aggregate)
    data = {'report': report, 'title':report.verbose_name, 'for_csv':for_csv, 'range':range(cant_of_group),'cant_of_group':cant_of_group +1}
    return render_to_response('reporting/view.html', data, 
                              context_instance=RequestContext(request))
    
def get_csv(request,slug):
    report = reporting.get_report(slug)(request)
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=xpot_report_'+ date.today().isoformat() +'.csv'
    
    row_csv = []    
    writer = csv.writer(response)
    # GENERATE HEADERS #
    
    if report.show_details:
        headers = report.get_details_headers()
        row_csv.append(report.get_headers()[0].text)
        for header in headers:
            row_csv.append(str(header))
    else:     
        headers = report.get_headers()
        for header in headers:
            row_csv.append(header.text)
    writer.writerow(row_csv)
    
    for row in report.results:
        
        if report.show_details:
            row_csv = []
            for value in row['details']:
                row_csv = []
                row_csv.append(row['values'][0])
                for final in value:
                    row_csv.append(final)
                writer.writerow(row_csv)
        else:
            row_csv = []
            for value in row['values']:
                row_csv.append(value)
            writer.writerow(row_csv)
    row_csv = []
    if report.show_details:
        headers = report.get_details_headers()
    else:
        headers = report.get_headers()
    cant_of_group = len(headers) - len(report.aggregate)

    row_csv = []
    for i in range(0,cant_of_group):
        row_csv.append('')
    if report.show_details:
        row_csv.append('')
    for title, value in report.get_aggregation():
        row_csv.append(title + ':' + str(value))
    writer.writerow(row_csv)
                    
    return response