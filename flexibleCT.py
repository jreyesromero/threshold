#!/usr/bin/env python
import sys
import json
import argparse
import os
import subprocess
import re
import string
from datetime import datetime

def parse_arguments():
    """
    Parser for command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File containing relationship between "
                                             "path and componetns.", required=True)
    parser.add_argument("-t1", "--tag1", help="Initial git TAG to obtain source differences."
                                              "ie: CQA_CI_0-MAIN_CQA", required=True)
    parser.add_argument("-t2", "--tag2", default="HEAD", \
                        help="Second git TAG to obtain source differences."
                             "HEAD TAG by default.")

    return parser.parse_known_args()

def get_commited_sources(origingTag, destTag):
    cmd = 'git diff %s..%s --name-only' % (origingTag, destTag)
    cmd_output = subprocess.check_output(cmd, shell=True).split()
    path_list = [path.decode('UTF-8') for path in cmd_output]
    return path_list

def read_reference_file(path):
    with open(path, 'r') as ctfile:
        ct_ref_file = [ref_line.rstrip('\n') for ref_line in ctfile.readlines()]
        return ct_ref_file

def get_component_list(path_changes_list, ct_file):
    ct_list = []
    reference_file = read_reference_file(ct_file)
    dir_name_list = [os.path.dirname(component_path) for component_path in path_changes_list]
    for dir_name in dir_name_list:
        ct_matching_list = [ct_line for ct_line in reference_file if dir_name in ct_line]
        for ct_match in ct_matching_list:
            component = ct_match.split(' ',1)[0]
            if component not in ct_list:
                ct_list.append(component)
    return ct_list

def main():
    options, _ = parse_arguments()
    src_changes_list = get_commited_sources(options.tag1, options.tag2)
    list_of_components = get_component_list(src_changes_list, options.file)
    print("list_of_components {}".format(list_of_components))

if __name__ == '__main__':
    try:
        sys.exit(main())
    except EnvironmentError as env_error:
        print ("EnvironmentErro: {}".format(str(env_error)))
        sys.exit(2)
