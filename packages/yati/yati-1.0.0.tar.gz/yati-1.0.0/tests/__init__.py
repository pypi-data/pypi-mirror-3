"""These are where all the automated tests for Yati will be stored"""

import os
import unittest
from yati import Yati


class YatiTestBase(unittest.testcase):
    """The base class for all Yati tests"""

    def setUp(self):
        """All this does right now is initialize Yati"""
        self.yati = Yati()
        self.userhome = os.getenv("HOME")
