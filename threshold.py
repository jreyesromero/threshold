  #!/usr/bin/env python
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

    print("%5s %50s %10s %10s %10s   %s" % ("PHASE", "PROCEDURE", "RUNTIME", "THRESHOLD", "DIFF", "VERDICT"))
    for line in lfile.readlines():

      read_line = line.split()
      phase, procedure, time = read_line[0], read_line[1], read_line[2]
      threshold_time = read_threshold_json_file(threshold_file, phase, procedure)

      if threshold_time is None:
        diff_str = "N/A"
        verdict = "Not found"
      else:
        diff = diff_percentage(time, threshold_time)
        verdict = "OK" if abs(diff) <= 10 else "WARNING"
        diff_str = "%+.2f%%" % diff
      print("%5s %50s %10s %10s %10s   %s" % (phase, procedure, time, threshold_time, diff_str, verdict))

  def diff_percentage(process_run_time, process_threshold_time):
    t1_secs = convert_string_to_seconds(process_run_time)
    t2_secs = convert_string_to_seconds(process_threshold_time)
    result_secs = (t1_secs - t2_secs)

    if t1_secs ==0 and t2_secs == 0:
      return 0
    elif t1_secs == 0:
      return float("-inf")
    elif t2_secs == 0:
      return float("inf")
    else:
      return ((t1_secs - t2_secs)/float(t2_secs))*100.0

  def convert_string_to_seconds(input_time):
    time = datetime.strptime(input_time,"%H:%M:%S")
    return get_time_in_seconds(time)


  def get_time_in_seconds(time):
    secs = time.second + 60 * (time.minute + 60*time.hour)
    return secs

  if __name__ == '__main__':
      options, args = parse_arguments()
      treat_log_file(options.log_file, options.threshold)

