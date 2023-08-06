# -*- coding: utf-8 -*-
import os
import sys

from quotachecker.cmd_input import cmd_input


def test_no_opts_no_args():
    sys.argv = [sys.argv[0]]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == []
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == None


def test_csv_file():
    sys.argv = [sys.argv[0], "-f", "result.csv"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == "result.csv"
    assert arg_opts.folder == []
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == None


def test_folder():
    sys.argv = [sys.argv[0], "fold-1", "fold-2"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == ["fold-1", "fold-2"]
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == None


def test_human_human_readable():
    sys.argv = [sys.argv[0], "-r"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == []
    assert arg_opts.human_readable == True
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == None


def test_overwrite():
    sys.argv = [sys.argv[0], "-o"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == []
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == True
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == None


def test_start_folder():
    sys.argv = [sys.argv[0], "-s", "start_to_quote"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == []
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == "start_to_quote"
    assert arg_opts.text_file == None


def test_text_file():
    sys.argv = [sys.argv[0], "-t", "textfile.txt"]
    arg_opts = cmd_input()
    assert arg_opts.csv_file == None
    assert arg_opts.folder == []
    assert arg_opts.human_readable == False
    assert arg_opts.overwrite == False
    assert arg_opts.start_folder == os.getcwd()
    assert arg_opts.text_file == "textfile.txt"
