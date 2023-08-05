#!/usr/bin/env python

import sys
###
from selenium import webdriver
###
from parse_sel import parse_sel
from webdriver_commands import WebdriverCommands

def log(text):
    print(text)


def selexe(fp):
    """
    fp: fp to selenium 'sel' file
    """
    driver = webdriver.Firefox()
    #import pdb;pdb.set_trace()
    driver.implicitly_wait(30)
    wdc = WebdriverCommands(driver, 'http://localhost:8080')
    try:
        for command, target, value in parse_sel(fp):
            log('%s(%s, %s)' % (command, target, value))
            func = getattr(wdc, 'wd_'+command)
            if not func:
                raise RuntimeError('no proper function for sel command "%s" implemented' % command)
            func(target, value)
    finally:
        driver.quit()

if __name__ == '__main__':
    selFilename = sys.argv[1]
    selexe(open(selFilename))
