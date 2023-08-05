from unittest2 import TestCase

from agar.url import uri_for
from agar.test import BaseTest, WebTest

import main

class MainTest(BaseTest, WebTest):

    APPLICATION = main.application

    def test_hello_world(self):
        response = self.get("/")
        self.assertOK(response)
