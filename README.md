# DMARC-Buddy

DMARC-Buddy is a collection of scripts designed to be run on shared hosting
servers that will process DMARC reports in to summaries you can read. The
goal is to have something easy to run on common servers that provides basic,
yet immediate over views.

After Workspaces shutdown I needed to start monitoring emails for several
domains to ensure emails were being sent from all users. Some were multihosted
domains on my account, some on other servers. Some were domains that should not
send any emails, and some where domains that were important for small businesses
or custom domains for friends. I needed the ability to see this all at no
cost, because I didn't make any profit hosting these websites.

Features:
- Downloads and saves DMARC-Reports immediately
- Processes DMARC-Reports and make a summary log per domain, per month
- Process summary logs to get a 28 day trend, and total for this month and last
- Web page dashboard of all domain recent activity, linked to summary logs
- Web page monthly summary logs for each domain, linked to individual reports
- The summary log web view shows email sources that have failed SPF or DKIM
- Web page view of XML report, formatted for reading and easily downloaded
- Unlimited domains

Reports are grouped by date recieved (not for reporting period). This way a
report that comes in several days late is not missed with looking at recent
reports. I don't see the value of combined charts or graphs that show a 
percentage of failures, so I'm not planning to include those.

## Requirements

- Python 2 from the scripts that process the reports and data files. Tested on 2.7.5.
- Linux to run the shell script that prepares the reports for processing
- PHP for the XML, log and overview viewers.
- Appache for the above viewers

## Design approach for compatibility

My goal was to make something that can be run on the vast majority of shared
hosting environment. This resulted in me making some specific decisions,
some of which I'm not sure I'm comforatable with.

The easiest way to do this would have been to write it all in PHP. But I
decided to balance that with using the best tool for the job. That's
why I used a combination of Python, shell scripting and PHP. I would be
pleased if people added support for different ways of doing this,
allowing users to choose ways that worked best for them.

**Linux and shell scripting**: My impression is that most shared hosting
servers run on Linux, thus the key is to us cron job (which can be set in
cPanel, for example) that run a shell script (.sh).

**Python 2**: Most shared hosts seem to have Python 2 be the default
interpreter. Many seem to use `virtualenv` to be able to change Python
versions. It's unclear to me how common this is, and the setup is
strange for people who are new to Python or used to running it on
dedicated hardware.

Currently this has been tested on Python 2.7.5. The scripts are so small
that attack vectors should be minimal. I would like to have these run
on a more secure Python 3 intepreter. I need more information on how
wide spread they are among popular webhosts.

**PHP 7.x**: Many large and well maintained PHP web apps are not yet compatible
with PHP 8 and so many people need to stay on PHP 7. So the dashboard, domain
summaries and XML viewer are all handled with PHP 7 compatible code.

**Email forwarder piped to script**: Finally, I wanted something that was
immediate and straightforward. For this reason I choose to use a Python script
that is feed an email directly, and saves it. Rather than the setup required to
sign in to a IMAP account and complexity to download emails. Also, I've
discovered that some reports are misleading with time and date stamps, and have
attachments with no bodies, appears as single-part emails. Though I'm open to
such a solution being included in the future.

If the server that the DMARC reports go to is different and cannot be changed,
you could have that server setup a forwarder for the account by the server
forwarders setting or in the email account setting up a forwarding option,
or filter.


## Installation


### Prepare Files

1. Create a folder that is not accessible by the web, or if it is accessible by the web password protected.
  Or, I suppose, some URL with a [random string](https://www.random.org/strings/) on the end, like
  `example.com/not-dmarc-buddy-UVKHdemr6z`. If it's not accessible by the web you won't be able to view
  the summary webpages.

2. Extract the downloaded archive in that folder.


### Configure cPanel

3. Create a cron job that runs `sh/process-dmarc-reports.sh -p /path/to/dmarc-buddy` daily or hourly.
    I like to have it run at 23 hours 59 minutes or * hours 59 minutes so it correctly identifies
    the date the report was recieved.

4. Create an email forwarder that pipes the email to 
  `python /home/user/path/dmarc-buddy/save-dmarc-attachments.py -p /path/to/dmarc-buddy`


### Configure SPF, DKIM and DMARC

5. Create DMARC entries that send reports to the forwarder setup in #4.
  
Going to the web facing URL for the dmarc-buddy folder should show the dashboard, with
links to logs, which link to individual reports. This won't work until the
`sh/process-dmarc-reports.sh` script has run at least once after a report have been received.



## Usage / View logs

If you find some fails and want to know more, you can load the report XML, and press Control-S to save it locally.
Then use a free service to upload that log to and see if they have any insight:

* https://easydmarc.com/tools/dmarc-aggregated-reports



## Possible future features

- Email on report with a fail.
- IMAP downloading might be good, but I don't plan to add this feature myself.