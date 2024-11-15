#!/bin/python
import os, sys, getopt
import xml.etree.ElementTree
from datetime import datetime
from socket import gethostbyaddr, herror

# Parse the argv (argument vector) parameters
# To get the path, in the future maybe a debug mode
def parse_parameters(PATH):
    try:
        options = "hf:p:e:"
        long_options = ["Help", "File=", "Path=", 'Echo=']
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
            
        for opt, arg in opts:
            if opt in ("-p", "--Path"):
                PATH = arg
            if opt in ("-f", "--File"):
                file = arg
            elif opt in ("-e", "--Echo"):
                print("echo: "+arg)
                exit(1)
            elif opt in ("-h", "--Help"):
                print("python parse-dmarc-report.py -p /home/username/path-to-dmarc-buddy -f /home/username/path-to-report/file.xml")
                exit(2)
    except getopt.error as err:
        print(str(err))
        exit(2)
    return PATH, file

PATH = '.'
PATH, file = parse_parameters(PATH)
DATA_PATH = PATH+'/data'


# Open report
date_recieved = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
month_recieved = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m")
report = xml.etree.ElementTree.parse(file).getroot()

# Find namespace
# Some reports use a DMARC 2.0 name space, despite being in draft
# eg: <feedback xmlns="urn:ietf:params:xml:ns:dmarc-2.0">
if report.tag == "feedback":
    ns = ""
elif report.tag == "{urn:ietf:params:xml:ns:dmarc-2.0}feedback":
    ns = '{urn:ietf:params:xml:ns:dmarc-2.0}'
else:
    print("Error: Unrecognized name space")
    print('Namespace', report.tag)
    exit(1)

# Report metadata
report_filename = os.path.basename(file)

try:
    report_org = report.find(ns+'report_metadata/'+ns+'org_name').text
    report_id = report.find(ns+'report_metadata/'+ns+'report_id').text
    source_domain = report.find(ns+'policy_published/'+ns+'domain').text
    date_start = report.find(ns+'report_metadata/'+ns+'date_range/'+ns+'begin').text
    date_end = report.find(ns+'report_metadata/'+ns+'date_range/'+ns+'end').text
except AttributeError:
    print('AttributeError', "Cannot find metadata")
    exit(1)



date_start = datetime.fromtimestamp(float(date_start)).strftime("%Y-%m-%d %H:%M:%S")
date_end = datetime.fromtimestamp(float(date_end)).strftime("%Y-%m-%d %H:%M:%S")

for record in report.findall(ns+'record'):
    source_ip = record.find(ns+'row/'+ns+'source_ip').text
    try:
        name, alias, addresslist = gethostbyaddr(source_ip)
    except herror:
        name = "Unknown/None"
    source_ip_lookup = name
    count = record.find(ns+'row/'+ns+'count').text

    # SPF policy evaluation, DKIM result
    spf_eval = record.find(ns+'row/'+ns+'policy_evaluated/'+ns+'spf')  
    if spf_eval is not None:
        spf_eval = spf_eval.text
    else:
        spf_eval = ''
    
    spf_result = record.find(ns+'auth_results/'+ns+'spf/'+ns+'result')
    if spf_result is not None:
        spf_result = spf_result.text
    else:
        spf_result = ''

    # DKIM policy evaluation, DKIM result
    dkim_eval = record.find(ns+'row/'+ns+'policy_evaluated/'+ns+'dkim')
    if dkim_eval is not None:
        dkim_eval = dkim_eval.text
    else:
        dkim_eval = ''

    dkim_result = record.find(ns+'auth_results/'+ns+'dkim/'+ns+'result')
    if dkim_result is not None:
        dkim_result = dkim_result.text
    else:
        dkim_result = ''

    envelope_from = record.find(ns+'identifiers/'+ns+'envelope_from')
    if envelope_from is not None:
        envelope_from = envelope_from.text
    else:
        envelope_from = ''
    header_from = record.find(ns+'identifiers/'+ns+'header_from')
    if header_from is not None:
        header_from = header_from.text
    else:
        header_from = ''
    dkim_domain = record.find(ns+'auth_results/'+ns+'dkim/'+ns+'domain')
    if dkim_domain is not None:
        dkim_domain = dkim_domain.text
    else:
        dkim_domain = ''
    spf_domain = record.find(ns+'auth_results/'+ns+'spf/'+ns+'domain')
    if spf_domain is not None:
        spf_domain = spf_domain.text
    else:
        spf_domain = ''

    # Append result to log 
    log = ( date_recieved+"\t"+ 
        date_start+"\t"+date_end+"\t"+report_org+"\t"+report_id+"\t"+ 
        count+"\t"+spf_eval+"\t"+spf_result+"\t"+dkim_eval+"\t"+dkim_result+"\t"+ 
        source_ip+"\t"+source_ip_lookup+"\t"+
        envelope_from+"\t"+header_from+"\t"+spf_domain+"\t"+dkim_domain+"\t"+
        report_filename 
        +"\n" )
    
    domain_log = open(DATA_PATH+'/'+month_recieved+'-'+source_domain+'.log', 'a')
    domain_log.write(log)
    domain_log.close()
    
    all_log = open(DATA_PATH+'/'+month_recieved+'-all.log', 'a')
    all_log.write(log)
    all_log.close()

exit(0)