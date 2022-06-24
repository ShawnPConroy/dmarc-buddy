# DMARC-Buddy

DMARC-Buddy is a collection of scripts designed to be run on shared hosting
servers that will process DMARC reports in to summaries you can read.

Requirements:

- Python 2 from the scripts that process the reports and data files. Tested on 2.7.5.
- Linux to run the shell script that prepares the reports for processing
- PHP for the XML, log and overview viewers.
- Appache for the above viewers

My approach was to make something that can be run on the vast majority of shared
hosting environment. I found that Python 3 and PHP 8 had limited compatibility and
was is often complicated for new users, so I'm
making it on PHP 7.x and Python 2.x, at least for now. Also, using email
forwarder piping to process the email, rather than accessing IMAP, which
seemed more complicated. If needed the receiving email server can forward
reports to another computer to process it.

I decided to use the best tool for the job that is widely availble. Rather than
use say, PHP for everything, I decided to use shell scripts and Python for processing,
and PHP for displaying the summaries.

## Installation

1. Create a folder that is not accessible by the web, or if it is accessible by the web password protected.
  Or, I suppose, some URL with a [random string](https://www.random.org/strings/) on the end, like
  `example.com/not-dmarc-buddy-UVKHdemr6z`. If it's not accessible by the web you won't be able to view
  the summary webpages.

2. Extract the downloaded archive in that folder.

3. Create a cron job that runs `sh/process-dmarc-reports.sh -p /path/to/dmarc-buddy` daily or hourly.
    I like to have it run at 23 hours 59 minutes or * hours 59 minutes so it correctly identifies
    the date the report was recieved.

4. Create an email forwarder that pipes the email to 
  `python /home/user/path/dmarc-buddy/save-dmarc-attachments.py -p /path/to/dmarc-buddy`

5. Create DMARC entries that send reports to the forwarder setup in #4.
  
Going to the web facing URL for the dmarc-buddy folder should show the dashboard, with
links to logs, which link to individual reports. This won't work until the
`sh/process-dmarc-reports.sh` script has run at least once after a report have been received.





## Uses forwarders

I was hoping to make something that would be most applicable to people running off a shared hosting environment, rather than a multiserver complicated setup. That said, DMARC reports can always have a forwarders set to a separate server it can be run on.

Also, you can just have it email to that server directly in the DMARC record.


## Possible future features

- Email on report with a fail.
- IMAP downloading might be good, but I don't plan to add this feature myself.