#!/usr/bin/env python
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
    parser.add_argument("-t", "--threshold", default="threshold.json", \
                        help="json file with threshold information. ie: threshold.json.")

    return parser.parse_known_args()

def read_threshold_json_file(json_file, phase_id, proc_name):
    """
    Function to read the threshold json file

    @param json_file path of file in json format containing threshold values for every procedure
    @param phase_id  name of the phase
    @param proc_name name of the procedure. We have to take the threshold time for that procedure

    @return threshold_time read for a given procedure
    """
    try:
        with open(json_file, 'r') as jfile:
            threshold_params = json.load(jfile)
            for phase in threshold_params.get("phases", []):
                if phase["name"] == phase_id:
                    for proc in phase['procedures']:
                        if proc['proc_id'] == proc_name:
                            return proc['run_time']
    except EnvironmentError:
        raise

def treat_log_file(log_file, threshold_file):
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
        print("%5s %50s %10s %10s %10s   %s" % ("PHASE", "PROCEDURE", "RUNTIME", \
                                                "THRESHOLD", "DIFF", "VERDICT"))
        with open(log_file, 'r') as lfile:
            for line in lfile.readlines():
                read_line = line.split()
                phase, procedure, time = read_line[0], read_line[1], read_line[2]
                threshold_time = read_threshold_json_file(threshold_file, phase, procedure)

                if threshold_time is None:
                    diff_str = "N/A"
                    verdict = "Not found"
                else:
                    diff = diff_percentage(time, threshold_time)
                    verdict = "OK" if abs(diff) <= PERCENT_RANGE else "WARNING"
                    diff_str = "%+.2f%%" % diff

                print("%5s %50s %10s %10s %10s   %s" % (phase, procedure, time, \
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

    :return:
    """
    options, args = parse_arguments()
    treat_log_file(options.log_file, options.threshold)

if __name__ == '__main__':
    PERCENT_RANGE = 10
    try:
        sys.exit(main())
    except EnvironmentError as io_exception:
        print >> sys.stderr, str(io_exception)
        sys.exit(2)
