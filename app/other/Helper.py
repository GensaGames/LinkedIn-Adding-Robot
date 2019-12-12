import os
import pickle

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, \
    TimeoutException, WebDriverException, StaleElementReferenceException
import logging


##########################################
def save_session(cookies):
    if not os.path.exists(SESSION_PATH):
        os.makedirs(SESSION_PATH)

    with open(SESSION_PATH + SESSION_NAME, "wb") as file:
        pickle.dump(cookies, file)


SESSION_NAME = 'session.txt'
SESSION_PATH = os.path.abspath(
    __file__ + "/../../../resource/")


def find_one_of(driver, *args):
    for loc in args:
        try:
            element = driver.find_element_by_xpath(loc)
            if element is not None:
                return element
        except (NoSuchElementException, WebDriverException) as e:
            logging.error("Error on Finding Objects: {}".format(e))


def get_text_excluding_children(driver, element):
    return driver.execute_script("""
        return jQuery(arguments[0]).contents().filter(function() {
            return this.nodeType == Node.TEXT_NODE;
        }).text();
        """, element)


##########################################
def get_session():
    location = os.path.join(SESSION_PATH, SESSION_NAME)
    logging.info('Use next location for Cookies: '
                 + str(location))
    if not os.path.exists(location):
        return []
    with open(location, "rb") as file:
        return pickle.load(file)



