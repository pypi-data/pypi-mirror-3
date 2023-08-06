# -*- coding: utf-8 -*-
"""Folder Quota Checker

This program returns the quota of 1st level sub folders in a directory using
the ``du`` command (available on all \*nix platforms).
"""

import os
import subprocess
import sys

from cmd_input import cmd_input
from csv_output import _csv_output


def _get_size(name, human_readable=False):
    """Return the size of the given name using 'du -s' by default"""
    # store the size from the shell command "du -sh ."
    if human_readable:
        du_option = "-sh"
    else:
        du_option = "-sk"
    shell_du = subprocess.Popen(["du", du_option, os.path.realpath(name)],
        stdout=subprocess.PIPE)
    return shell_du.communicate()[0].split('\t')[0]


def read_textfile(textfile):
    """Gives the lines of a file as a list"""
    f = open(textfile, "r")
    content = f.read()
    f.close()
    # All filenames without line brakes
    lines = content.split("\n")
    # Remove blank lines and return
    return [i for i in lines if i != '']


def _output(data, namespace):
    csv_file = namespace.csv_file
    overwrite = namespace.overwrite

    if csv_file:
        _csv_output(data, csv_file, overwrite)
    else:
        for i in data:
            sys.stdout.write("%s %s\n" % tuple(i[:2]))


def _main(namespace):
    """Check which options are enabled and work with the given options and args
    """
    # The namespaces
    start_folder = namespace.start_folder
    text_file = namespace.text_file
    folder = namespace.folder
    human_readable = namespace.human_readable

    folder_quotas = []
    # get folders list
    # all entry's in start folder
    for i in sorted(os.listdir(start_folder)):
        i_joind_path = os.path.join(start_folder, i)
        # when folder
        if os.path.isdir(i_joind_path):
            # no folder selection
            if not text_file and not folder:
                folder_quotas.append(
                    (i, _get_size(i_joind_path, human_readable))
                )
            # folder from text file and the folder name
            if text_file and len(folder) > 0:
                raise Exception("Cant use -t and directory names together.")
#                sys.exit(2)
            elif text_file and i in read_textfile(text_file):
                # quot folder and append it
                quote = (i, _get_size(i_joind_path, human_readable))
                folder_quotas.append(quote)
            # when no folder from text file it is possible to give arguments
            if not text_file and len(folder) > 0:
                if i in folder:
                    quote = (i, _get_size(i_joind_path, human_readable))
                    folder_quotas.append(quote)
    return folder_quotas


def main():
    namespace = cmd_input()
    data = _main(namespace)
    _output(data, namespace)

if __name__ == "__main__":
    main()
