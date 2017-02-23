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
#        print("Phase name: {} ".format(phase))
#        print("Procedure name: {}".format(procedure))
#        print("Time: {}".format(time))
    threshold_time = read_threshold_json_file(threshold_file, phase, procedure)
    if threshold_time is None:
      print("Run time for process not found for phase {} proc {}".format(phase,procedure))
    else:
      print("RUNTIME {} threshold {}".format(time,threshold_time))
#      check_run_time(time, threshold_time)
      if diff_times_in_seconds(time, threshold_time):
        print("Difference inside 10 percent allowed")
      else:
        print("percentage difference excedes 10 percent allowed")

def diff_times_in_seconds(process_run_time, process_threshold_time):
  time1 = datetime.strptime(process_run_time,"%H:%M:%S")
  time2 = datetime.strptime(process_threshold_time,"%H:%M:%S")
  h1, m1, s1 = time1.hour, time1.minute, time1.second
  h2, m2, s2 = time2.hour, time2.minute, time2.second
  t1_secs = s1 + 60 * (m1 + 60*h1)
  t2_secs = s2 + 60 * (m2 + 60*h2)
  print("run_time_seconds {} threshold_seconds {}".format(t1_secs, t2_secs))
  result_secs = ( t1_secs - t2_secs)

  # if result_secs > 0 : process_run_time higher than threshold
  # if result_secs < 0 : process_run_time less than threshold
  # in both case, lets check if the difference is higher than 10%
  if result_secs != 0: 
    diff_percentage = abs(((t2_secs - t1_secs)/t2_secs)*100.0)
    print("percentage {}".format(diff_percentage))
    if diff_percentage > 10:
       return False

  return True

if __name__ == '__main__':
    options, args = parse_arguments()
#    run_time = read_threshold_json_file(options.threshold, 'SV', 'PROC_SYSTEM_UPGRADE_PREPARATION')

#    for descriptor in phases:
#        phase_name = descriptor.get("name")
#        procedures = descriptor.get("procedures",[])

    treat_log_file(options.log_file, options.threshold)
        
