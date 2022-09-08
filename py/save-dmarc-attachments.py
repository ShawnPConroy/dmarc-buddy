#!/usr/bin/python

import getopt
import sys
import email
import uuid
from datetime import datetime
from time import strftime
from os.path import splitext

PATH = '.'

REPORT_TYPES = {'text/xml', 'application/x-gzip', 'application/gzip',
    'application/zip', 'application/x-zip'}

# Parse the argv (argument vector) parameters
# To get the path, in the future maybe a debug mode
def parse_parameters(PATH):
    email_filename = ""
    try:
        options = "hp:e:f:"
        long_options = ["Help", "Path=", 'Echo=','File=']
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
            
        for opt, arg in opts:
            if opt in ("-p", "--Path"):
                PATH = arg
            elif opt in ("-e", "--Echo"):
                print("echo: "+arg)
                exit(1)
            elif opt in ("-f", "--File"):
                print("Running from file")
                email_filename = arg
            elif opt in ("-h", "--Help"):
                print("python save-dmarc-attachments.py -p /home/username/path-to-dmarc-buddy")
                exit(2)
    except getopt.error as err:
        print(str(err))
        exit(2)
    
    return PATH, email_filename

# How emails are regularly processed
def email_from_pipe():
    full_msg = ""
    for line in sys.stdin:
        full_msg += line
    return email.message_from_string(full_msg)

# For testing purposes
def email_from_file(filename):
    f = open(filename, 'r')
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
            file_name, file_ext = splitext(part.get_filename())
            if (file_ext == '.gz'):
                file_ext = ".xml.gz"
                file_name = file_name[:-4]
            f = open(REPORT_PATH+file_name+'-'+str(uuid.uuid4())+file_ext, 'w')
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

PATH, email_filename = parse_parameters(PATH)
REPORT_PATH = PATH + '/downloads/'
LOG_PATH = PATH + '/logs/'
TEST_PATH = PATH + '/tests/'

if email_filename == "":
    msg = email_from_pipe()
else:
    msg = email_from_file(email_filename)

downloads, parts, ctypes = download_reports(msg, REPORT_PATH, REPORT_TYPES)
add_to_log(msg, downloads, parts, ctypes, LOG_PATH)