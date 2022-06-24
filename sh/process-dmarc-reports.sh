#!/bin/bash

# Prepares downloaded attachments, run the Python script to process them,
# and then runs the Python script to pull stats for use with the web views.


# Set to path to this folder (no trailing slash)
DB_PATH=.
mode=none
# Ignore empty wildcard results and folders
shopt -s nullglob


# Backs up attachments and extracts archives
function prepare_reports {

    # Prepare Reports from downloads, using loops to avoid not found errors
    if [ show_debugging == "true" ]
    then
        echo "Preparing reports"
        echo "-----------------"
        echo
    fi

    rsync -a ${verbose} ${REPORT_PATH} ${BACKUP_ATTACHMENTS}

    for archive in ${REPORT_PATH}/*.gz
    do
        gzip ${verbose} -d ${archive}
    done

    for archive in ${REPORT_PATH}/*.zip
    do
        unzip $archive -d ${REPORT_PATH}/
        if [ $? -eq 0 ]
        then
            rm ${verbose} $archive
        fi
    done    
}


# Runs all reports through the script that logs key data
function process_reports {
    # Process Reports
    if [ show_debugging == "true" ]
    then
        echo
        echo "Procesing files"
        echo "---------------"
    fi

    # Stop if no xml files. This stops the for statement below from processing
    # all files in the dmarc-buddy main folder. It gets a list of all files,
    # then checks if it's count zero. If so, exist.
    file_list=(${FOLDER}/*.xml)
    if [ ${#file_list[*]} -eq 0 ]
    then
        if [ show_debugging == "true" ]
        then
            echo " - No reports found. Exiting."
        fi
        return
    fi

    if [ show_debugging == "true" ]
    then
        echo " - Found ${#file_list[*]} file(s)"
    fi
    # Go through files in order of when they were received
    for report in `ls -rt ${FOLDER}/*.xml`
    do
        python ${PYTHON_SCRIPT_PATH}/parse-dmarc-report.py -p ${DB_PATH} -f ${report}
        if [ $? -eq 0 ]
        then
            if [ show_debugging == "true" ]
            then
                echo " - Processed $report"
            fi
            if [ "$mode" == "typical" ]
            then
                # archive reports
                mv ${verbose} -n $report $ARCHIVE_PATH
            fi
        else
            echo " - Failed to parse $report"
        fi
    done

    # Show file not moved on success
    for leftover in ${REPORT_PATH}/*
    do
        echo " - Leftover $leftover"
    done
    echo 
}

# Find basic for the current month, for use with the web views.
function process_logs {
    # Process logs
    if [ show_debugging == "true" ]
    then
        echo
        echo "Process Logs"
        echo "------------"
        echo
    fi
    python ${PYTHON_SCRIPT_PATH}/generate-dmarc-stats.py -p ${DB_PATH}
}






# Get parameters, setup environment
use_archive=false
show_debugging=true
verbose=""

while getopts adp: option
do 
    case "${option}"
        in
        a)use_archive=true;;
        d)
            show_debugging=true
            verbose="-v"
            ;;
        p)DB_PATH=${OPTARG};;
    esac
done

REPORT_PATH=${DB_PATH}/downloads
ARCHIVE_PATH=${DB_PATH}/reports
LOGS_PATH=${DB_PATH}/data
PYTHON_SCRIPT_PATH=${DB_PATH}/py
BACKUP_ATTACHMENTS=${DB_PATH}/backup-downloads

if [ show_debugging == "true" ]
then
    echo
    echo "======================="
    echo "Run saved DMARC Reports"
    echo "======================="
    echo
    echo
    echo "Using path ${DB_PATH}"
    echo
fi

# Here we go, let us do this:
if [ "$use_archive" == "false" ]
then
    # Run report as usual
    mode="typical"
    FOLDER=${REPORT_PATH}
    prepare_reports
    process_reports
    process_logs
else
    # Perform report on archive folder
    echo "Run archives"
    echo
    mode="archive"
    FOLDER=${ARCHIVE_PATH}
    process_reports
    process_logs
fi

if [ show_debugging == "true" ]
then
    echo
fi