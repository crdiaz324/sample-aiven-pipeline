#!/usr/bin/env python
# Portions of this file were borrowed from https://github.com/confluentinc/examples 

import argparse, sys

def parse_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(
             description="Python producer to Aiven Kafka")
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-f',
                          dest="config_file",
                          help="path to configuration file",
                          required=True)
    required.add_argument('-t',
                          dest="topic",
                          help="topic name",
                          required=True)
    args = parser.parse_args()

    return args

def read_config(config_file):
    """Read the client configuration file"""

    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()

    return conf
