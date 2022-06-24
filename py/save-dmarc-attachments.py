#!/usr/bin/python

import getopt
import sys
import email
from datetime import datetime
from time import strftime

PATH = '.'

REPORT_TYPES = {'text/xml', 'application/x-gzip', 'application/gzip',
    'application/zip', 'application/x-zip'}

# Parse the argv (argument vector) parameters
# To get the path, in the future maybe a debug mode
def parse_parameters(PATH):

    try:
        options = "hp:e:"
        long_options = ["Help", "Path=", 'Echo=']
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
            
        for opt, arg in opts:
            if opt in ("-p", "--Path"):
                PATH = arg
            elif opt in ("-e", "--Echo"):
                print("echo: "+arg)
                exit(1)
            elif opt in ("-h", "--Help"):
                print("python save-dmarc-attachments.py -p /home/username/path-to-dmarc-buddy")
                exit(2)
    except getopt.error as err:
        print(str(err))
        exit(2)
    
    return PATH

# How emails are regularly processed
def email_from_pipe():
    full_msg = ""
    for line in sys.stdin:
        full_msg += line
    return email.message_from_string(full_msg)

# For testing purposes
def email_from_file():
    f = open(PATH+'test-email.txt', 'r')
    full_msg = f.read()
    f.close()

    return email.message_from_string(full_msg)

def download_reports(msg, REPORT_PATH, REPORT_TYPES):
    downloads = 0
    parts = 0
    ctypes = "";
    
    # If email has parts, download any possible DMARC reports
    for part in msg.walk():
        ctype = part.get_content_type()
        parts += 1
        if ctype in REPORT_TYPES:
            downloads += 1
            f = open(REPORT_PATH+part.get_filename(), 'w')
            f.write(part.get_payload(decode=True))
            f.close()
        ctypes += '\n\t\t'+ctype+' : '+str(part.get_filename())
    return str(downloads), str(parts), ctypes

def add_to_log(msg, downloads, parts, ctypes, LOG_PATH):
    weekNum = datetime.now().strftime("%Yweek%W")

    # Log parts for bug testing and confirmation
    f = open(LOG_PATH + weekNum + '-attachments.log', 'a')
    f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    f.write("\n\tFrom: " + msg['from'])
    f.write("\n\tSubject: " + msg['subject'])
    f.write("\n\t" + msg['date'])
    f.write("\n\tDownloaded " + ' [' + str(downloads) + ' of ' + str(parts) + '] ')
    f.write("\n\tContent types: " + ctypes)
    f.write('\n')
    f.close()

PATH = parse_parameters(PATH)
REPORT_PATH = PATH + '/downloads/'
LOG_PATH = PATH + '/logs/'
TEST_PATH = PATH + '/tests/'

msg = email_from_pipe()
downloads, parts, ctypes = download_reports(msg, REPORT_PATH, REPORT_TYPES)
add_to_log(msg, downloads, parts, ctypes, LOG_PATH)