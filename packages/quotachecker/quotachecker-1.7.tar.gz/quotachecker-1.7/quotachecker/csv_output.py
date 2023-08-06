# -*- coding: utf-8 -*-

import csv
import datetime
import os
import sys


def _write_line(content, add, overwrite=False):
    """Append to content or replace

    append when overwrite is false,
    replace the last element when overwrite is true"""
    if overwrite == True:
        content[-1] = add
    else:
        content.append(add)
    return content


def _read_csv(csv_file="output.csv", seperator=";"):
    """Read csv_file and make a dict"""
    if os.path.isfile(csv_file):
        os.system("cp %s %s~" % (csv_file, csv_file))
        with open(csv_file, "rb") as f:
            reader = csv.reader(f, delimiter=seperator)
            content = [i for i in reader]
    else:
        content = [["directorys", ], ]
    return content


def _write_csv(content_list, csv_file="output.csv"):
    with open(csv_file, "wb") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerows(content_list)
    pass


def _make_datestamp(date=None):
    """Give a string with the actually date stamp"""
    if date is None:
        date = datetime.date.today()
    return date.strftime("%Y-%m")


def _add_data(new_content, file_content, datestamp, overwrite=False):
    """Append the current data to the given out file"""

    new_content = dict(new_content)
    line_length = None
    date_written = False
    for line in file_content:
        folder_name = line[0]
        if not date_written:
            # Row already exist
            if datestamp == line[-1] and overwrite == True:
                # Overwrite only when the header already exist
                overwrite = True
            elif datestamp == line[-1] and overwrite == False:
                note = """
    The column that should be written in the csv-file already exist.
    use the "-o" option if you want to OVERWRITE it.\n"""
                sys.stdout.write(note)
                raise SystemExit(1)
            else:
                # Dont overwrite, append
                overwrite = False

            # Add time header
            _write_line(line, datestamp, overwrite)

            # count for new folder lines
            line_length = len(line)
            date_written = True

        elif folder_name in new_content.keys():
            _write_line(line, new_content.pop(folder_name), overwrite)
        else:
            _write_line(line, 0, overwrite)
    # folder names who are not in the existing csv-file
    if len(new_content) > 0:
        for fold, value in new_content.iteritems():
            # read "0" for all existing columns
            new_row = [fold] + ["0" for i in range(line_length - 2)] + [value]
            file_content.append(new_row)
    return file_content


def _csv_output(new_data, csv_file="output.csv", overwrite=False):
    file_content = _read_csv(csv_file)
    datestamp = _make_datestamp()
    data = _add_data(new_data, file_content, datestamp, overwrite)
    _write_csv(data, csv_file)
