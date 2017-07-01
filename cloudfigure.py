﻿import boto3
import argparse
import os
import sys
import json

is_running_as_script = __name__ == "__main__"

def file_exists(path):
    return os.path.exists(path)

def read_all_text(path):
    with open(path, 'r') as myfile:
        data = myfile.read().replace('\n', '')
    return data

class ConfigValue:
    def __init__(self, name, location, unencrypt):
        self.name = name
        self.location = location
        self.unencrypt = unencrypt

class CloudfigureFile:
    def __init__(self):
        self.configuration = []
        self.substitute_into = []
    def add_config_value(self, config_value):
        self.configuration.append(config_value)
    def add_substitute_into(self, substitute_into):
        self.substitute_into.append(substitute_into)

def parse_cloudfigure_file(config_json):
    config = CloudfigureFile()
    json_obj = json.loads(config_json)

    for config_value in json_obj['Configuration']:
        name = config_value["Name"]
        location = config_value["Location"]
        if "Unencrypt" in config_value:
            unencrypt = config_value["Unencrypt"]
        else:
            unencrypt = False
        config_val = ConfigValue(name, location, unencrypt)
        config.add_config_value(config_val)

    for substitute_into in json_obj['SubstituteInto']:
        config.add_substitute_into(substitute_into)

    return config 

def run_cloudfigure(boto, cloudfigure_config, stack_ids, assume_role=None, verbose=False):
    print("Running Cloudfigure.")
    if assume_role is not None:
        print("Assume IAM role - " + assume_role)
        sts = boto.client('sts')
        try:
            sts_role = sts.assume_role(RoleArn=assume_role, RoleSessionName="Cloudfigure")
        except Exception as e:
            print("Error - failed to assume role")
            print(e)
            sys.exit(1)
        print("Assumed role")

    kms = boto.client('kms')
    cfn = boto.client('cloudformation')
    
    


def run_cloudfigure_script(boto, args):
    verb = args.verbose
    if args.assume_role != None:
        print("Assume role")
    else:
        if verb: print("Dont assume role")

    if verb: print("Cloudfigure file is located at: " + args.cloudfigure_file)
    if file_exists(args.cloudfigure_file):
        if verb: print("file exists.")
        cloudfigure_config = read_all_text(args.cloudfigure_file)
    else:
        print("Error - file doesn't exist at " + args.cloudfigure_file)
        sys.exit(1)

    if len(args.stack_ids) < 1:
        print("No stack ids specified in call, try look for them in file")
        if args.stack_ids_in_file is None:
            print("Error - please provide at least 1 stack id or specify file location")
            sys.exit(1)
        else:
            print("stack ids file is located at: " + args.stack_ids_in_file)
            if file_exists(args.stack_ids_in_file):
                if verb: print("file exists.")
            else:
                print("Error - file doesn't exist")
                sys.exit(1)
    else:
        stack_ids = args.stack_ids
        if verb: print("Stack id(s) are:")
        for stack_id in args.stack_ids:
            if verb: print(" - " + stack_id)

    run_cloudfigure(boto, cloudfigure_config, stack_ids, args.assume_role, args.verbose)

if is_running_as_script:
    # don't want to run if importing as module
    PARSER = argparse.ArgumentParser(description='arguments for cloudfigure')
    PARSER.add_argument('--assume_role', nargs='?',
                        help='Optionally assume IAM role to get config, enter full aws arn.')
    PARSER.add_argument('--cloudfigure_file', nargs='?', default='./Cloudfigure.json',
                        help='Specify cloudfigure file, defaults to ./Cloudfigure.json')
    PARSER.add_argument('--stack_ids', nargs='+', default=[], help='StackId(s) of initial stack')
    PARSER.add_argument('--stack_ids_in_file', nargs='?',
                        help='StackId(s) as a json array, in text file at specified location.')
    PARSER.add_argument('--verbose', '-v', action='store_true', help='log more stuff')

    run_cloudfigure_script(boto3, PARSER.parse_args())
