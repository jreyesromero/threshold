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

def read_threshold_json_file(json_file):
    try:
        jfile = open(json_file, 'r')
    except IOError:
        print >> sys.stderr, "Error, cannot open " + json_file + " for reading."
        sys.exit(1)


    threshold_params = json.load(jfile)
    jfile.close()


    phases = threshold_params.get("phases", [])
    return phases

def treat_log_file(log_file, threshold_file):
    try:
        lfile = open(log_file, 'r')
    except IOError:
        print >> sys.stderr, "Error, cannot open " + log_file + " for reading."
        sys.exit(1)

    for line in lfile.readlines():
        read_line = line.split()
        phase, procedure, time = read_line[0], read_line[1], read_line[2]
        print("Phase name: {} ".format(phase))
        print("Procedure name: {}".format(procedure))
        print("Time: {}".format(time))

        

if __name__ == '__main__':
    options, args = parse_arguments()
    phases = read_threshold_json_file(options.threshold)
#    for descriptor in phases:
#        phase_name = descriptor.get("name")
#        procedures = descriptor.get("procedures",[])

    treat_log_file(options.log_file, options.threshold)
        
