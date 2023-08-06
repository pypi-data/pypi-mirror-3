# -*- coding: utf-8 -*-

import pytest

import quotachecker as qcheck
from quotachecker import csv_output


class TestInit():
    """Test the functionality in the '__init__.py'
    """
    TestNamespace = type("TestNamespace", (), {})  # class

    def setup_method(self, module):
        """Multi used values"""
        # 1016k
        self.du_content = ("0" * 64 + "\n") * 32 * 500

    def test_read_texfile(self, tmpdir):
        """Test read text file"""
        textfile = tmpdir.mkdir("sub").join("text file.txt")
        content = """
folder0.txt
folder1.txt
folder2.txt
folder3.txt
folder4.txt
folder5.txt"""
        textfile.write(content)
        read_content = [
            "folder0.txt",
            "folder1.txt",
            "folder2.txt",
            "folder3.txt",
            "folder4.txt",
            "folder5.txt"
        ]
        assert qcheck.read_textfile(str(textfile)) == read_content

    def test_get_size(self, tmpdir):
        du_testfile = tmpdir.mkdir("sub").join("du_file.txt")
        du_testfile.write(self.du_content)

        human_readable = False
        assert qcheck._get_size(str(du_testfile), human_readable) == "1016"

        human_readable = True
        assert qcheck._get_size(str(du_testfile), human_readable) == "1016K"

    def test_output(self, tmpdir, capsys):
        """Test output"""

        # output per csv
        out_csv = tmpdir.mkdir("sub").join("output.csv")
        self.TestNamespace.csv_file = str(out_csv)
        self.TestNamespace.overwrite = False
        data = (("dic-1", 100), ("dic-2", 200))
        namespace = self.TestNamespace
        qcheck._output(data, namespace)
        assertation_content = [
            ["directorys", csv_output._make_datestamp()],
            ["dic-2", "200"],
            ["dic-1", "100"],
        ]
        csv_content = csv_output._read_csv(namespace.csv_file)
        assert csv_content == assertation_content

        # output stout
        self.TestNamespace.csv_file = None
        namespace = self.TestNamespace
        qcheck._output(data, namespace)
        out, err = capsys.readouterr()
        assert out == u"dic-1 100\ndic-2 200\n"

    def test_main(self, tmpdir, capsys):
        """Test main"""
        checkdir = tmpdir.mkdir("sub")

        # Test the main function
        # Different directories to test
        checkdir_count = 5

        data_file = checkdir.join("copyme.txt")
        data_file.write(self.du_content)
        files = ["file{0}.txt".format(i) for i in range(checkdir_count)]

        # make the check dirs 'drc' for directory
        for drc in range(len(files)):
            path = checkdir.mkdir("check{0}".format(drc))
            # copy files 'fil' for files
            for fil in range(drc + 1):
                copy_to = path.join("file{0}.txt".format(fil))
                data_file.copy(copy_to)

        self.TestNamespace.start_folder = str(checkdir)
        self.TestNamespace.text_file = False
        self.TestNamespace.folder = []
        self.TestNamespace.human_readable = False
        namespace = self.TestNamespace

        assertation_content = [
            ('check0', '1016'),
            ('check1', '2032'),
            ('check2', '3048'),
            ('check3', '4064'),
            ('check4', '5080')]
        assert qcheck._main(namespace) == assertation_content

        # Test with text file.txt that stores folder names
        # The textfile
        tfile = checkdir.join("textfile.txt")
        # Emty lines should be ignored
        tfile.write(u"check0\n\ncheck2")
        self.TestNamespace.start_folder = str(checkdir)
        self.TestNamespace.text_file = str(tfile)
        self.TestNamespace.folder = []
        self.TestNamespace.human_readable = False
        namespace = self.TestNamespace
        assertation_content = [('check0', '1016'), ('check2', '3048')]
        assert qcheck._main(namespace) == assertation_content

        # Test folder names as arguments
        tfile.write(u"check0\n\ncheck2")
        self.TestNamespace.start_folder = str(checkdir)
        # In this case it should be not allowed to give folder names with
        # text file. This should be fail!!
        self.TestNamespace.text_file = str(tfile)
        self.TestNamespace.folder = ['check0', 'check3', 'check4']
        namespace = self.TestNamespace
        with pytest.raises(Exception):
            qcheck._main(namespace)

        self.TestNamespace.text_file = None
        namespace = self.TestNamespace
        assertation_content = [
            ('check0', '1016'),
            ('check3', '4064'),
            ('check4', '5080')]
        assert qcheck._main(namespace) == assertation_content
