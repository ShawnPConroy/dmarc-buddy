#!/bin/python

# Generates monthly stats from log files.
#
# Usage:
#   python generate-dmarc-stats.py -p /home/username/path-to-dmarc-buddy"

from sys import argv
import csv, json
import os, getopt
import datetime

DATE_RECIEVED = 0
DATE_START = 1
DATE_END = 2
REPORT_ORG = 3
REPORT_ID = 4
COUNT = 5
SPF_EVAL = 6
SPF_RESULT = 7
DKIM_EVAL = 8
DKIM_RESULT = 9
SOURCE_IP = 10
SOURCE_IP_LOOKUP = 11
ENVELOPE_FROM = 12
HEADER_FROM = 13
SPF_DOMAIN = 14
DKIM_DOMAIN = 15
REPORT_FILENAME = 16

PATH = '.'

# Parse the argv (argument vector) parameters
# To get the path, in the future maybe a debug mode
def parse_parameters(path):

    try:
        options = "hf:p:e:"
        long_options = ["Help", "File=", "Path=", 'Echo=']
        opts, args = getopt.getopt(argv[1:], options, long_options)
            
        for opt, arg in opts:
            if opt in ("-p", "--Path"):
                path = arg
            elif opt in ("-e", "--Echo"):
                print("echo: "+arg)
                exit(1)
            elif opt in ("-h", "--Help"):
                print("python generate-dmarc-stats.py -p /home/username/path-to-dmarc-buddy")
                exit(2)
    except getopt.error as err:
        print(str(err))
        exit(2)
    
    return path


def generate_monthly_json(month, data_path):
    monthly_stats = process_logs(month, data_path)
    f = open(data_path+"/"+str(month)+"-monthly.json", 'w')
    f.write(json.dumps(monthly_stats))
    f.close()


def process_logs(month, data_path):
    domain_stats = dict()
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith('.log') and file.startswith(month):
                domain_stats[file[8:-4]] = process_domain_csv(root+'/'+file)
    
    return domain_stats


def process_domain_csv(file):
    stats = dict()
    
    stats['pass'] = dict()
    stats['pass']['sources'] = dict()
    stats['pass']['count'] = 0
    stats['pass']['0'] = 0
    stats['pass']['1'] = 0
    stats['pass']['2'] = 0
    stats['pass']['3'] = 0
    stats['pass']['4'] = 0
    stats['pass']['5'] = 0
    stats['pass']['6'] = 0
    stats['pass']['7'] = 0
    stats['pass']['last7'] = 0
    stats['pass']['last28'] = 0

    stats['fail'] = dict()
    stats['fail']['sources'] = dict()
    stats['fail']['count'] = 0
    stats['fail']['0'] = 0
    stats['fail']['1'] = 0
    stats['fail']['2'] = 0
    stats['fail']['3'] = 0
    stats['fail']['4'] = 0
    stats['fail']['5'] = 0
    stats['fail']['6'] = 0
    stats['fail']['7'] = 0
    stats['fail']['last7'] = 0
    stats['fail']['last28'] = 0

    stats['lastReport'] = datetime.datetime.strptime("2022-02-22 20:22:02", "%Y-%m-%d %H:%M:%S")

    f = open(file)
    log = csv.reader(f, delimiter="\t")
    
    for record in log:
        record_date = datetime.datetime.strptime(str(record[DATE_RECIEVED]), "%Y-%m-%d %H:%M:%S").date()
        record_time = datetime.datetime.strptime(str(record[DATE_RECIEVED]), "%Y-%m-%d %H:%M:%S")
        if record_time > stats['lastReport']:
            stats['lastReport'] = record_time;
        days_ago = str((datetime.date.today() - record_date).days)
        if record[SPF_EVAL] == record[SPF_RESULT] == record[DKIM_EVAL] == record[DKIM_RESULT] == "pass":
            status = "pass"
        else:
            status = "fail"

        stats[status]['count'] += int(record[COUNT])

        domains = set()
        
        if record[DKIM_DOMAIN]: domains.add(record[DKIM_DOMAIN])
        if record[SPF_DOMAIN]: domains.add(record[SPF_DOMAIN])
        if record[DKIM_DOMAIN]: domains.add(record[DKIM_DOMAIN])
        if record[HEADER_FROM]: domains.add(record[HEADER_FROM])

        for domain in domains:
            if domain not in stats[status]['sources']:
                stats[status]['sources'][domain] = dict()
            stats[status]['sources'][domain][record[SOURCE_IP]] = record[SOURCE_IP]
        
        if int(days_ago) > 0 and int(days_ago) <= 28:
            stats[status]['last28'] += int(record[COUNT])
            if int(days_ago) > 0 and int(days_ago) <= 7:
                stats[status]['last7'] += int(record[COUNT])
                stats[status][days_ago] += int(record[COUNT])
        elif int(days_ago) == 0:
            stats[status][days_ago] += int(record[COUNT])
    
    f.close()
    stats['lastReport'] = stats['lastReport'].strftime("%Y-%m-%d %H:%M:%S")

    return stats

PATH = parse_parameters(PATH)
DATA_PATH = PATH+'/data'

# This month:
this_month = datetime.date.today()
last_month = this_month - datetime.timedelta(days=this_month.day)
this_month = this_month.strftime("%Y-%m")
last_month = last_month.strftime("%Y-%m")
generate_monthly_json(last_month, DATA_PATH)
generate_monthly_json(this_month, DATA_PATH)