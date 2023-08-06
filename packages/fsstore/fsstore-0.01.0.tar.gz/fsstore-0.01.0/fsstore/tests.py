# -*- coding: utf-8 -*-

import unittest
from tempfile import mkdtemp
from fsstore.core import Store


class TestInterface(unittest.TestCase):
    def setUp(self):
        "Initialize a Store with a temporary directory."
        self.tempdir = mkdtemp()
        self.fs = Store(self.tempdir)

    def test_save_string(self):
        "Test that simple string-assignment works."
        self.fs["hello"] = "world"
        self.assertEquals(self.fs["hello"], "world")
        self.assertEquals(self.fs.get("hello"), "world")

    def test_save_dict(self):
        "Test that we can save a dict and get it again."
        self.fs["dir"] = {"a": "b"}
        self.assertEquals(self.fs["dir"]["a"], "b")
    
    def test_nested_dicts(self):
        "Test that we can save nested dicts and retrieve their contents."
        self.fs["dir"] = {"x": {"y": "z"}}
        self.assertEquals(self.fs["dir"]["x"]["y"], "z")

    def test_reassignment_dict_to_string(self):
        """Test that nothing breaks if we assign something that used to be a
        dict to a string.
        """
        self.fs["dir"] = {"x": {"y": "z"}}
        self.fs["dir"] = "a new thing."
        self.assertEquals(self.fs["dir"], "a new thing.")

    def test_reassignment_string_to_dict(self):
        """Test that nothing breaks if we assign something that used to be a
        string to a dict.
        """
        self.fs["dir"] = "an old thing."
        self.fs["dir"] = {"x": {"y": "z"}}
        self.assertEquals(self.fs["dir"]["x"]["y"], "z")

    def test_resume(self):
        "Test that results are constant across Stores."
        second = Store(self.tempdir)
        self.fs["constant"] = "5"
        self.assertEquals(self.fs["constant"], second["constant"])

    def test_get_file(self):
        self.fs["x"] = "yz"
        with self.fs.get_file("x") as f:
            self.assertEquals(f.read(), self.fs["x"], "yz")

