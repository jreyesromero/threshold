#!/usr/bin/env python
"""
This script gets the difference between two git tags, in terms of list of modified files.
After that, it will obtain the corresponding CT component for every path. To achieve this,
it will be necessary to configure the relation <CT component> - <code path> in a file.

After the modified components have been detected, the script will create a properties file
which can be useful for a jenkins job execution: CT testing execution only for those components
detected as modified by this script.

"""
import sys
import argparse
from os import getenv, path, chdir, getcwd
import subprocess

WORKSPACE = getenv('WORKSPACE', '.')
CT_PROPERTIES_FILE = path.join(WORKSPACE)
CUDB_REPO_PATH = "../cudb/"

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

def get_commited_sources(origin_tag, dest_tag):
    """
    Function which receives two git tags and extract the differences between them in terms
    of modified files.

    @param origin_tag TAG ORIGIN
    @param dest_tag DESTINATION TAG

    @return list of path files which correspond to the differences between the two tags.
    """
    CWD = getcwd()
    chdir(CUDB_REPO_PATH)
    cmd = 'git diff %s..%s --name-only' % (origin_tag, dest_tag)
    cmd_output = subprocess.check_output(cmd, shell=True).split()
    path_list = [path.decode('UTF-8') for path in cmd_output]
    chdir(CWD)
    return path_list

def read_reference_file(ref_file_path):
    """
    Function which reads the content of the reference_file. This file stores the relation
    between every path of the source code and its corresponding CT component.

    @param path of the reference_file

    @return content of the reference_file as a list
    """
    with open(ref_file_path, 'r') as ctfile:
        ct_ref_file = [ref_line.rstrip('\n') for ref_line in ctfile.readlines()]
        return ct_ref_file

def get_non_duplicated_components(ct_matching_list, ct_list):
    """
    Every line in the ct_macthing_list is obtained after having compared every path of the
    modified files with the reference file. Every line will have the next syntax:
    <COMPONENT> <ASSOCIATED_PATH>

    This function reads, for every matching line from the reference file, the corresponding
    component, and checks if that component has been alredy inserted in the returned list.
    If that's not the case, this function will include the component in ct_list

    @param ct_matching_list List of lines from reference_file which have matched with the path
                            of the modified files.
    @param ct_list List of components previously matched. To guarantee non duplicated values.

    @return list of CT components modified. Non duplicated componentes guaranteed.
    """
    for ct_match in ct_matching_list:
        component = ct_match.split(' ', 1)[0]
        if component not in ct_list:
            ct_list.append(component)
    return ct_list

def compare_ref_with_dirname(reference_file, dir_name_list):
    """
    Intermediate function to get a list of modified CT components.
    It will compares every path of the modified files with a reference file.
    Reference file must relate every path of the code with its corresponding component.

    @param reference_file path of the file with the relation between paths and CT components.
    @param dir_name_list list of the paths of the files which have been modified.
                         This list includes only 'sources' or 'ToolsFW' paths

    @return list of CT components modified. Non duplicated componentes guaranteed..
    """
    ct_list = []
    for dir_name in dir_name_list:
        ct_matching_list = [ct_line for ct_line in reference_file \
                            if ct_line.split(' ', 1)[1] in dir_name]
        ct_list = get_non_duplicated_components(ct_matching_list, ct_list)
    return ct_list

def get_component_list(path_modifications_list, ct_file):
    """
    Function to get the list of modified CT components.

    @param path_modifications_list list of paths of modified files.
    @param ct_file path of baseline file which relates every path with a CT component.

    @return list of CT components modified. Will indicated what are the test suites to run.
    """
    reference_file = read_reference_file(ct_file)
    dir_name_list = [path.dirname(component_path) for component_path in path_modifications_list]
    # second parameter just include 'sources' and 'ToolsFW' paths
    return compare_ref_with_dirname(reference_file, \
                                    [dir_line for dir_line in dir_name_list \
                                     if "sources" in dir_line or "ToolsFW" in dir_line])

def write_ct_properties_file(ct_true, ct_false):
    """
    Function to write a properties file which indicates with TRUE value all those components
    that must be run during the execution of CT job in jenkins.

    @param ct_true components to be set to TRUE
    @param ct_flase components to be set to FALSE
    """
    properties_file = open(path.join(CT_PROPERTIES_FILE, 'run_ct.properties'), 'w')
    for comp_true in ct_true:
        properties_file.write(comp_true + '=TRUE\n')

    for comp_false in ct_false:
        properties_file.write(comp_false + '=FALSE\n')

    properties_file.close()

def configure_ct_properties_file(ct_run_list, ct_list):
    """
    Function to prepare the configuration to be written to ct_properties file.

    @param ct_run_list components checked as to be run
    @param ct_list complete list of ct components
    """
    ct_true = []
    ct_false = []
    for ct_component in ct_list:
        if ct_component in ct_run_list:
            ct_true.append(ct_component)
        else:
            ct_false.append(ct_component)
    write_ct_properties_file(ct_true, ct_false)

def main():
    """
    Main function
    """
    ct_list = ["CS", "LDAPFE", "IMM", "RECONC", "SRCC", "CAPACITYHANDLER", \
               "TRAFFCTRL", "NOTIFICATIONS", "SM"]
    options, _ = parse_arguments()
    modifications_list = get_commited_sources(options.tag1, options.tag2)
    list_of_components = get_component_list(modifications_list, options.file)
    configure_ct_properties_file(list_of_components, ct_list)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except EnvironmentError as env_error:
        print("EnvironmentError: {}".format(str(env_error)))
        sys.exit(2)
