#!/bin/bash

# Prepares downloaded attachments, run the Python script to process them,
# and then runs the Python script to pull stats for use with the web views.


# Set to path to this folder (no trailing slash)
DB_PATH=.
mode=none
# Ignore empty wildcard results and folders
shopt -s nullglob




# Runs all reports through the script that logs key data
function process_emails {
    
    # Process Reports
    if [ ${show_debugging} == "true" ]
    then
        echo
        echo "Procesing files"
        echo "---------------"
    fi

    # Stop if no xml files. This stops the for statement below from processing
    # all files in the dmarc-buddy main folder. It gets a list of all files,
    # then checks if it's count zero. If so, exist.
    file_list=(${EMAIL_PATH}/*)
    if [ ${#file_list[*]} -eq 0 ]
    then
        if [ ${show_debugging} == "true" ]
        then
            echo " - No reports found. Exiting."
        fi
        return
    fi

    if [ ${show_debugging} == "true" ]
    then
        echo " - Found ${#file_list[*]} file(s)"
    fi

    # Go through files in order of when they were received
    i=0
    for email in `ls -rt ${EMAIL_PATH}/*`
    do
        python ${PYTHON_SCRIPT_PATH}/save-dmarc-attachments.py -p ${DB_PATH} -f ${email}
        if [ $? -eq 0 ]
        then
            if [ ${show_debugging} == "true" ]
            then
                echo " - Processed $email"
            fi
        else
            echo " - Failed to parse $email"
        fi
        i=$((i+1))
    done


}





# Get parameters, setup environment
use_archive=false
show_debugging=true
verbose=""

while getopts dp:f: option
do 
    case "${option}"
        in
        f)email_folder=${OPTARG};;
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
EMAIL_PATH=${DB_PATH}/${email_folder}

echo ${show_debugging}

if [ ${show_debugging} == "true" ]
then
    echo
    echo "======================="
    echo "Process DMARC emails"
    echo "======================="
    echo
    echo
    echo "Using path ${EMAIL_PATH}"
    echo
fi



# Run report as usual
mode="typical"
FOLDER=${REPORT_PATH}
process_emails



if [ ${show_debugging} == "true" ]
then
    echo
fi
