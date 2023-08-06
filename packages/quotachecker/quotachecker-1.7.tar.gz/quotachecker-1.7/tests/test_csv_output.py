# -*- coding: utf-8 -*-
import datetime
import pytest

from quotachecker.csv_output import _write_line, _read_csv, _write_csv
from quotachecker.csv_output import _make_datestamp, _add_data, _csv_output


class TestCsvOutput():
    def setup_method(self, module):
        self.csv_content = [
            ["directorys", "2012-03"],
            ["directory-01", "1000"],
            ["directory-02", "2000"],
            ["directory-03", "3000"],
        ]
        self.raw_csv_content = u"""directorys;2012-03
directory-01;1000
directory-02;2000
directory-03;3000"""

    def test_write_line(self):
        """Test write line with overwriting true"""
        content = [0, ]
        add = 1

        # with overwrite True
        assert _write_line(content, add, True) == [1]

        # with overwrite False
        content = [0, ]
        assert _write_line(content, add, False) == [0, 1]

    def test_read_csv(self, tmpdir):
        """Test read_csv"""
        csv_file = tmpdir.mkdir("sub").join("test.csv")
        csv_file.write(self.raw_csv_content)
        assert _read_csv(str(csv_file)) == self.csv_content
        assert _read_csv("not_exist.csv") == [["directorys", ], ]

    def test_write_csv(self, tmpdir):
        """Test write_csv"""
        out_csv = tmpdir.mkdir("sub").join("out.csv")
        # Write a new file
        _write_csv(self.csv_content, str(out_csv))
        # Test whether exist
        assert _read_csv(str(out_csv)) == self.csv_content

    def test_make_datestamp(self):
        assert _make_datestamp() == datetime.date.today().strftime("%Y-%m")

    def test_add_data(self):
        """Test _add_data with new not exist file"""

        # Test overwrite existing columns
        new_content = (\
            ("directory-03", 3001),)
        overwriten_content = [
            ["directorys", "2012-03"],
            ["directory-01", 0],
            ["directory-02", 0],
            ["directory-03", 3001],
        ]
        datestamp = "2012-03"
        overwrite = True
        assert _add_data(new_content, self.csv_content,
            datestamp, overwrite) == overwriten_content

        # Test column exist but False overwrite
        csv_content = overwriten_content
        datestamp = "2012-03"
        overwrite = False
        with pytest.raises(SystemExit):
            _add_data(new_content, csv_content, datestamp, overwrite)

        # Test a not existing dictionary with is not in the csv_file
        new_content = (("new_dict", 4000), )
        csv_content = [
            ["directorys", "2012-03"],
            ["directory-01", 0],
            ["directory-02", 0],
            ["directory-03", 3001],
        ]
        datestamp = "2012-04"
        overwrite = False
        assert_content = [
            ["directorys", "2012-03", "2012-04"],
            ["directory-01", 0, 0],
            ["directory-02", 0, 0],
            ["directory-03", 3001, 0],
            ["new_dict", "0", 4000],
        ]
        assert _add_data(new_content, self.csv_content,
            datestamp, overwrite) == assert_content

    def test_csv_output(self, tmpdir):
        """Test csv_output
        """
        new_data = [
            ("directory-01", "1111"),
            ("directory-02", "2222"),
            ("directory-03", "3333"),
        ]
        csv_file = tmpdir.mkdir("sub").join("test.csv")
        csv_file.write(self.raw_csv_content)
        overwrite = False
        assert_content = [
            ["directorys", "2012-03", datetime.date.today().strftime("%Y-%m")],
            ["directory-01", "1000", "1111"],
            ["directory-02", "2000", "2222"],
            ["directory-03", "3000", "3333"],
        ]
        _csv_output(new_data, str(csv_file), overwrite)
        assert _read_csv(str(csv_file)) == assert_content
