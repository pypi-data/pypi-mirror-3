import unittest
import pyramid
from pyramid.config import Configurator
from pyramid import testing

class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
