import sys
import json
import argparse

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
    run_time = read_threshold_json_file(threshold_file, phase, procedure)
    if run_time is None:
      print("Run time for process not found for phase {} proc {}".format(phase,procedure))
    else:
      print("RUNTIME found: {} for phase {} procedure {}".format(run_time, phase, procedure))

if __name__ == '__main__':
    options, args = parse_arguments()
#    run_time = read_threshold_json_file(options.threshold, 'SV', 'PROC_SYSTEM_UPGRADE_PREPARATION')

#    for descriptor in phases:
#        phase_name = descriptor.get("name")
#        procedures = descriptor.get("procedures",[])

    treat_log_file(options.log_file, options.threshold)
        
