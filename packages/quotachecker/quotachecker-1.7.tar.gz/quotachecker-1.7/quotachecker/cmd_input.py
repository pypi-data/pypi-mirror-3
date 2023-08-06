# -*- coding: utf-8 -*-

import argparse
import os


ARGUMENTS = {\
    ('-f', '--file'): {\
        'dest': 'csv_file',
        'help': 'Output in a csv-file. By default the name of the CSV output'\
                'file is "output.csv".',
        'default': None},
    ('-o', '--overwrite'): {\
        'dest': 'overwrite',
        'help': 'Overwrite the row if the row already exist.',
        'default': False,
        'action': 'store_true'},
    ('-r', '--human-readable'): {\
        'dest': 'human_readable',
        'help': 'Converts the output in a human readable form.',
        'default': False,
        'action': 'store_true'},
    ('-s', '--start-folder'): {\
        'help': 'Starts in an optional folder. Default it is the current one.',
        'dest': 'start_folder',
        'action': 'store',
        'default': os.getcwd(),
        'nargs': '?'},
    ('-t', '--textfile'): {\
        'dest': 'text_file',
        'help': 'An optional folder set written in an text file.',
        'default': None,
        'action': 'store'},
    ('folder',): {\
        'help': 'Optional folder set as arguments.',
        'nargs': '*'},
}


usage = '''Folder Quota Checker
%(prog)s returns the quota of 1st level sub folders in a directory using the
du command (available on all *nix platforms).
%(prog)s [options]'''


def cmd_input():
    """Get the options and arguments from the standard input"""
    parser = argparse.ArgumentParser()

    # add each option from the OPTION data structure and pass it to parser
    for arg in ARGUMENTS:
        # arg as an Option
        if len(arg) == 2:
            parser.add_argument(arg[0], arg[1], **ARGUMENTS[arg])
        # arg as an positional argument
        elif len(arg) == 1:
            parser.add_argument(arg[0], **ARGUMENTS[arg])

    return parser.parse_args()
