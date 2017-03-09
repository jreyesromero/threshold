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

def get_component_list(path_changes_list, ct_file):

    ct_list = []
    with open(ct_file, 'r') as ctfile:
        for ct in path_changes_list:
            dir_name = str(os.path.dirname(ct))
            print("dir_name {}".format(str(dir_name)))
            for line in ctfile.readlines():
                print("lines {}".format(line))
                #if str(dir_name) in line:
                if line.find(str(dir_name)) != -1:
                    print("Encontrada dirname {} en line {}".format(dir_name,lines))
                    component = line.split(' ',1)[0]
                    if component not in ct_list:
                        ct_list.append(component)

    print("ct_list: {}".format(ct_list))

def main():
    options, _ = parse_arguments()
    #src_changes_list = get_commited_sources("CQA_0339_20170307182742_ONE_TRACK_GREEN","HEAD")
    src_changes_list = get_commited_sources(options.tag1, options.tag2)
    print("src_changes_list: {}".format(src_changes_list))
    get_component_list(src_changes_list, options.file)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except EnvironmentError as env_error:
        print ("EnvironmentErro: {}".format(str(env_error)))
        sys.exit(2)
