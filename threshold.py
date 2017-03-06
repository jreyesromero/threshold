#!/usr/bin/env python

"""
This scripts obtains the time difference, in percentage, between the execution of a upgrade
procedures and a preconfigured threshold time information.
In order to obtain that difference, the script needs to receive as input the path of two files:
 - Path of the file with the runtime values for all the procedures involved in the upgrade.
       This file will be generated during the execution of the upgrade.
       The format of every line included in the file must be similar to:
           <PHASE_ID> <PROCEDURE_ID> <RUN_TIME HH:MM:SS>

 - Path of the file which contains the threshold time values for every procedure involved in
   the upgrade.
       This file has a json format and should be configured before executing this script.
       Threshold time will have the format HH:MM:SS

To calculate the difference, the script would execute the next steps:
    1.- Will store in a cache the content of the json file with threshold values.
    2.- For every line in upgrade procedures runtime file, will check if the json file stores
        information about that phase and procedure.
        2.-1 If the phase and procedure is found in threshold file: will obtain the difference
             between the 2 times in seconds, and calculate the difference in percentage.
        2.2. If the phase and procedure aren't found, VERDICT will be Not found
    3.- Once that the percentage difference for a given phase/procedure has been calculated,
        the script will check if the absolute value of the percentage is:
            3.1. Between 0% and 10%: VERDICT will be OK
            3.2. Higher than 10%: VERDICT will be WARNING. A manual checks needs to be done to
                 get the reason for the difference in runtime for that process.

The output that the user will obtain after executing the script would be similar to:

PHASE                                       PROCEDURE    RUNTIME  THRESHOLD       DIFF   VERDICT
SV                    PROC_SYSTEM_UPGRADE_PREPARATION   00:02:12   00:02:12     +0.00%   OK
-S                 PROC_IBU_INSTALL_EVIP_ENCAPSULATOR   00:00:00       None        N/A   Not found
NI            PROC_IBU_EXECUTE_CUDB_AUTOMATED_INSTALL   00:39:17   00:49:47    -21.09%   WARNING

"""

import sys
import json
import argparse
from datetime import datetime


def parse_arguments():
    """
    Parser for command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--log_file", default="upgradeProceduresTiming.log", \
                        help="log file with upgrade execution times."
                             "ie: upgradeProceduresTiming.log.")
    parser.add_argument("-t", "--threshold", default="p.json", \
                        help="json file with threshold information. ie: threshold.json.")

    parser.add_argument("-p", "--platform", type=str, choices=set(('FTNODE', 'BSP8100_GEP3')),
                        help="platform type", required=True)

    return parser.parse_known_args()

def read_threshold_json_file(json_file):
    """
    Function to read threshold json file

    @param json_file path of file in json format containing threshold values for every procedure

    @return content of json file
    """
    try:
        with open(json_file, 'r') as jfile:
            return json.load(jfile)
    except EnvironmentError:
        raise




def get_threshold_for_procedure(platform_list, phase_id, proc_name):
    """
    Function to read threshold json file

    @param threshold_params cache which contains the content of threshold json file
    @param phase_id  name of the phase
    @param proc_name name of the procedure. We have to take the threshold time for that procedure

    @return threshold time for a given procedure
    """
    phases_list = platform_list[0]['phases']
    phase_element_list = [element for element in phases_list if element['name'] == phase_id]
    if phase_element_list:
        procedures_dict = phase_element_list[0]['procedures']
        if procedures_dict and proc_name in procedures_dict:
            return procedures_dict[proc_name]

def treat_log_file(log_file, platform, threshold_params):
    """
    Function to get the if, for every line of log_file containing runtime for every procedure,
    it exceeds a 10% time threshold, comparing with times in threshold_file in json format.
    Every line read from log_file will be checked againts threshold_format.

    @param log_file path of the file which contains upgrade procedures runtime values.
    @param threshold_file path of the file which contains the threshold time information for
    upgrade procedures.

    @return prints a line indicating if the procedures runtime exceeds in inside 10% acceptable
            range comparing
    """
    try:
        print ("%5s %50s %10s %10s %10s %10s" % ("PHASE", "PROCEDURE", "RUNTIME", \
                                                 "THRESHOLD", "DIFF", "VERDICT"))

        platform_list = [
            platform_type
            for platform_type in threshold_params.get("platforms", [])
            if platform_type['platform_id'] == platform
        ]

        with open(log_file, 'r') as lfile:
            for line in lfile.readlines():
                read_line = line.split()
                phase, procedure, time = read_line[0], read_line[1], read_line[2]
                threshold_time = get_threshold_for_procedure(platform_list, phase, procedure)
                if threshold_time is None:
                    diff_str = "N/A"
                    verdict = "Not found"
                else:
                    diff = diff_percentage(time, threshold_time)
                    verdict = "OK" if abs(diff) <= PERCENT_RANGE else "WARNING"
                    diff_str = "%+.2f%%" % diff

                print ("%5s %50s %10s %10s %10s   %s" % (phase, procedure, time, \
                                                        threshold_time, diff_str, verdict))

    except EnvironmentError:
        raise

def diff_percentage(process_run_time, process_threshold_time):
    """
    Function to calculate the time percentage difference between two times

    @param process_run_time        runtime value in HH:MM:SS format for a given upgrade procedure
    @param process_threshold_time  threshold time value in HH:MM:SS format for a given
                                   upgrade procedure

    @return percentage difference between two input params times
    """
    t1_secs = convert_string_to_seconds(process_run_time)
    t2_secs = convert_string_to_seconds(process_threshold_time)

    if t1_secs == 0 and t2_secs == 0:
        return 0
    elif t1_secs == 0:
        return float("-inf")
    elif t2_secs == 0:
        return float("inf")
    else:
        return ((t1_secs - t2_secs)/float(t2_secs))*100.0

def convert_string_to_seconds(input_time):
    """
    Function to convert a string to seconds

    @param input_time string to be converted to seconds

    @return input_time converted to seconds
    """
    time = datetime.strptime(input_time, "%H:%M:%S")
    return get_time_in_seconds(time)


def get_time_in_seconds(time):
    """
    Function to convert a time in HH:MM:SS format to seconds

    @param input_time time in HH:MM:SS format to be converted to seconds

    @return input_time converted to seconds
    """
    secs = time.second + 60 * (time.minute + 60*time.hour)
    return secs

def main():
    """
    Main function
    """
    options, _ = parse_arguments()
    threshold_params = read_threshold_json_file(options.threshold)
    treat_log_file(options.log_file, options.platform, threshold_params)


if __name__ == '__main__':
    PERCENT_RANGE = 10
    try:
        sys.exit(main())
    except EnvironmentError as env_error:
        print ("EnvironmentErro: {}".format(str(env_error)))
        sys.exit(2)
