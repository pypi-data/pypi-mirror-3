import unittest
from selenium import webdriver


class SelexeTestCase(unittest.TestCase):
    baseURL = None
    Driver  = webdriver.Firefox

    def setUp(self):
        self.driver. = self.Driver()

    def tearDown(self):
        self.driver.quit()

