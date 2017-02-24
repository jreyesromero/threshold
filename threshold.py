import sys
import json
import argparse
from datetime import datetime, timedelta, date

def parse_arguments():
    """
    Parser for command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--log_file", default="upgradeProceduresTiming.log", help="log file with upgrade execution times. ie: upgradeProceduresTiming.log.")
    parser.add_argument("-t", "--threshold", default="threshold.json", help="json file with threshold information. ie: threshold.json.")
    global args
    options, args = parser.parse_known_args()
    return options, args

def read_threshold_json_file(json_file, phase_id, proc_name):
  try:
    jfile = open(json_file, 'r')
  except IOError:
    print >> sys.stderr, "Error, cannot open " + json_file + " for reading."
    sys.exit(1)

  threshold_params = json.load(jfile)
  jfile.close()

  for phase in threshold_params.get("phases", []):
    si_procedures = []
    if (phase["name"] == phase_id):
      for proc in phase['procedures']:
        if (proc['proc_id'] == proc_name):
          return  proc['run_time']

def treat_log_file(log_file, threshold_file):
  try:
    lfile = open(log_file, 'r')
  except IOError:
    print >> sys.stderr, "Error, cannot open " + log_file + " for reading."
    sys.exit(1)

  for line in lfile.readlines():
    
    read_line = line.split()
    phase, procedure, time = read_line[0], read_line[1], read_line[2]
    threshold_time = read_threshold_json_file(threshold_file, phase, procedure)

    if threshold_time is None:
      print("Run time for phase {} and proc {} NOT FOUND\n".format(phase,procedure))
    else:
      print("phase: {} procedure: {} process_runtime: {} threshold: {}".format(phase,procedure,time,threshold_time))
      if diff_times_in_seconds(time, threshold_time):
        print("  Difference inside 10 percent ALLOWED\n")
      else:
        print("  percentage difference excedes 10 percent allowed\n")

def diff_times_in_seconds(process_run_time, process_threshold_time):
  t1_secs = convert_string_to_seconds(process_run_time)
  t2_secs = convert_string_to_seconds(process_threshold_time)
  result_secs = (t1_secs - t2_secs)

  # if result_secs > 0 : process_run_time higher than threshold
  # if result_secs < 0 : process_run_time less than threshold
  # in both case, lets check if the difference is higher than 10%
  if result_secs != 0: 
    diff_percentage = abs(((t2_secs - t1_secs)/t2_secs)*100.0)
    print("percentage {}".format(diff_percentage))
    if diff_percentage > 10:
       return False

  return True

def convert_string_to_seconds(input_time):
  time = datetime.strptime(input_time,"%H:%M:%S")
  return get_time_in_seconds(time)


def get_time_in_seconds(time):
  secs = time.second + 60 * (time.minute + 60*time.hour)
  return secs

if __name__ == '__main__':
    options, args = parse_arguments()
    treat_log_file(options.log_file, options.threshold)
        
