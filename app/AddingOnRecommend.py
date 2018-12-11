import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import app.other.PageObjects as PageObjects
from selenium.webdriver.chrome.options import Options

from collections import deque
import app.other.Helper as Helper
from random import randint
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, \
    WebDriverException

import logging


class StartWorker:
    ITER_TO_RELOAD = 12

    def __init__(self):
        self.driver = None
        self.__skipp_elements = deque(maxlen=5)

    def start(self):
        options = Options()
        options.headless = True

        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-bypass-list=*")

        self.driver = webdriver.Chrome(
            executable_path='../driver/chromedriver',
            options=options)

        self.driver.get(PageObjects.LINK_BASE)
        return self

    def load_session(self):
        for cookie in Helper.get_session():
            self.driver.add_cookie(cookie)
        return self

    def save_session(self):
        StartWorker.waite_cookies_save()

        Helper.save_session(
            self.driver.get_cookies())
        self.driver.close()
        return self

    @staticmethod
    def waite_cookies_save():
        time.sleep(15)

    def to_recommend(self):
        logging_.info('Navigation to Contacts and Waite...')
        self.driver.get(PageObjects.LINK_RECOMMEND)
        time.sleep(2)
        return self

    def follow_actions(self):
        logging_.info('Start Following Actions!')
        for _ in range(0, StartWorker.ITER_TO_RELOAD):
            self.__call_pagination()

        self.__add_connections()

        self.to_recommend() \
            .follow_actions()

    def __call_pagination(self):
        logging_.info('Calling pagination Now...')

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
                logging_.info('Wrong Element: {}'
                              .format(connect))
                continue

            StartWorker.waite_add_connect()

            try:
                ActionChains(self.driver) \
                    .move_to_element(connect).click().perform()
                logging_.info('Working Element... Clicked.')
                self.__check_block_state()

            except (NoSuchElementException, WebDriverException) as e:
                logging_.error("Error on Adding: {}!"
                               .format(str(e)))

    def __check_block_state(self):
        StartWorker.waite_add_connect()
        logging_.info('Checking block State...')

        try:
            dialog = self.driver.find_element_by_xpath(
                PageObjects.BUTTON_R_CONNECT_BLOCK)

            if dialog.is_displayed:
                StartWorker.waite_add_connect()
                dialog.click()

                logging_.info('Out of Invites. Blocked state now.\n'
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
        worker.start().load_session()\
            .to_recommend().follow_actions()

    except (NoSuchElementException, WebDriverException) as e:
        logging_.error(
            'Error running main Task: {}!\n'
            'Reschedule Chrome Driver!'.format(str(e)))

        worker.driver.close()
        main(argv)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)-15s %(message)s')
    logging_ = logging.getLogger(os.path.basename(__file__))

    sys.setrecursionlimit(1001001)
    main(sys.argv)
