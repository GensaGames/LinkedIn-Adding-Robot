import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import app.other.PageObjects as PageObjects
from collections import deque
import app.other.Helper as Helper
from random import randint
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, \
    WebDriverException

import logging


class StartWorker:

    ITER_TO_RELOAD = 10

    def __init__(self):
        self.driver = None
        self.__skipp_elements = deque(maxlen=5)

    def start(self):
        self.driver = webdriver.Chrome(
            executable_path='../driver/chromedriver')
        self.driver.maximize_window()

        self.driver.get(PageObjects.LINK_BASE)
        for cookie in Helper.get_session():
            self.driver.add_cookie(cookie)
        return self

    def to_recommend(self):
        logging.info('Navigation to Contacts and Waite...')
        self.driver.get(PageObjects.LINK_RECOMMEND)
        time.sleep(2)
        return self

    def follow_actions(self):
        logging.info('Start Following Actions!')
        for _ in range(0, StartWorker.ITER_TO_RELOAD):
            self.__call_pagination()
            self.__add_connections()

        self.to_recommend()\
            .follow_actions()

    def __call_pagination(self):
        logging.info('Calling pagination Now...')

        ActionChains(self.driver) \
            .send_keys(Keys.END).perform()
        StartWorker.waite_scroll_pagination()

        ActionChains(self.driver) \
            .send_keys(Keys.HOME).perform()
        StartWorker.waite_scroll()

    @staticmethod
    def waite_scroll_pagination():
        time.sleep(2)

    @staticmethod
    def waite_scroll():
        time.sleep(2 * 2)

    def __add_connections(self):
        for connect in self.driver.find_elements_by_xpath(
                PageObjects.BUTTON_R_CONNECT):

            if not connect.is_displayed() or \
                    not connect.is_enabled():
                logging.info('Wrong Element: {}'
                             .format(connect))
                continue

            StartWorker.waite_add_connect()

            try:
                ActionChains(self.driver) \
                    .move_to_element(connect).click().perform()
                logging.info('Working Element...')
                self.__check_block_state()

            except (NoSuchElementException, WebDriverException) as e:
                logging.error("Error on Adding: {}!"
                              .format(str(e)))

    def __check_block_state(self):
        StartWorker.waite_add_connect()
        logging.info('Checking block State...')

        try:
            dialog = self.driver.find_element_by_xpath(
                PageObjects.BUTTON_R_CONNECT_BLOCK)

            if dialog.is_displayed:
                StartWorker.waite_add_connect()
                dialog.click()

                logging.info('Out of Invites. Blocked state now.\n'
                             ' Waite some time...')
                StartWorker.waite_block_state()

        except (NoSuchElementException, WebDriverException):
            pass

    @staticmethod
    def waite_add_connect():
        time.sleep(0.5)

    @staticmethod
    def waite_block_state():
        time.sleep(randint(20, 30))


def main(argv):
    worker = StartWorker()

    try:
        worker.start().to_recommend() \
            .follow_actions()

    except (NoSuchElementException, WebDriverException) as e:
        logging.error('Error running main Task: {}!\n'
                      'Reschedule Chrome Driver!'
                      .format(str(e)))
        worker.driver.close()
        main(argv)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.setrecursionlimit(1001001)
    main(sys.argv)
