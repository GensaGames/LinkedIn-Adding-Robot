import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import app.other.PageObjects as PageObjects
from collections import deque
import app.other.Helper as Helper
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, \
    WebDriverException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import logging


class StartWorker:
    def __init__(self):
        self.driver = None
        self.__skipp_elements = deque(maxlen=20)

    def start(self):
        options = Options()
        options.headless = False

        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-bypass-list=*")

        self.driver = webdriver.Chrome(
            executable_path='../driver/chromedriver-n.exe',
            options=options)

        self.driver.get(PageObjects.LINK_BASE)
        for cookie in Helper.get_session():
            if 'expiry' in cookie:
                del cookie['expiry']
            self.driver.add_cookie(cookie)
        return self

    def to_contacts(self):
        logging.info('Navigation to Contacts and Waite...')
        self.driver.get(PageObjects.LINK_CONTACTS)
        StartWorker.waite_page_load()
        return self

    @staticmethod
    def waite_page_load():
        time.sleep(3)

    def follow_actions(self):
        logging.info('Start Working Actions!')

        self.__look_next_element()
        self.__scroll_page()
        self.__check_end_page()
        self.follow_actions()

    def __look_next_element(self):
        for add_element in self.driver.find_elements_by_xpath(
                PageObjects.BUTTON_ADD_XPATH):
            if add_element in self.__skipp_elements:
                continue

            if not add_element.is_displayed() or \
                    not add_element.is_enabled():
                logging.info('Wrong Element: {}'
                             .format(add_element))
                continue

            logging.info('Working Element: {}'
                         .format(add_element))
            self._start_adding(add_element)

    def _start_adding(self, add_element):
        logging.info('Adding Working element!')
        StartWorker.waite_anim_action()

        try:
            ActionChains(self.driver)\
                .move_to_element(add_element).click().perform()
        except (NoSuchElementException, WebDriverException) as e:
            logging.error("Error on Adding: {}".format(str(e)))

        logging.info('Waite and Confirm Dialog!')
        try:
            StartWorker.waite_anim_action()
            send_now = WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable(
                    (By.XPATH, PageObjects.BUTTON_SEND_NOW_XPATH)))

            if PageObjects.BUTTON_SEND_TEXT not in \
                Helper.get_text_excluding_children(
                    self.driver, send_now):
                    raise NoSuchElementException()

            send_now.click()
            WebDriverWait(self.driver, 2).until(
                ec.invisibility_of_element_located(
                    (By.XPATH, PageObjects.BUTTON_SEND_NOW_XPATH)))
            StartWorker.waite_anim_action()

        except (NoSuchElementException, WebDriverException) as e:
            logging.error("Error on Confirm Add: {}".format(str(e)))
            self.__skipp_elements.append(add_element)
            self.__cancel_add()
            return

    @staticmethod
    def waite_anim_action():
        time.sleep(0.5)

    def __cancel_add(self):
        logging.info('Cancel and Waite Dialog...')
        try:
            self.driver.find_element_by_xpath(
                PageObjects.BUTTON_EMAIL_INVITE).click()
            StartWorker.waite_anim_action()
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(
                "Error on Cancelling Add: {}".format(str(e)))

    def __scroll_page(self):
        logging.info('Scroll Page and Waite...')
        action_scroll = ActionChains(
            self.driver).send_keys(Keys.ARROW_DOWN)
        for i in range(0, 6):
            action_scroll.perform()
        StartWorker.waite_anim_action()

    def __check_end_page(self):
        try:
            element = Helper.find_one_of(
                self.driver, PageObjects.BUTTON_NEXT_PAGE,
                PageObjects.BUTTON_NEXT_PAGE_1)

            is_end_page = self.driver.execute_script(
                "if((window.innerHeight+window.scrollY) >= "
                "document.body.offsetHeight){return true;}")

            if is_end_page and element.is_displayed():
                logging.info('Contacts Page Ended!')
                element.click()

                StartWorker.waite_load_page_next()
            else:
                logging.info('Should continue scrolling...')
        except (NoSuchElementException, WebDriverException) as e:
            logging.error(
                "Error on Checking End: {}".format(str(e)))

    @staticmethod
    def waite_load_page_next():
        time.sleep(2)

    def save_and_quite(self):
        Helper.save_session(
            self.driver.get_cookies())
        self.driver.quit()


def main(argv):
    worker = StartWorker()

    try:
        worker.start().to_contacts() \
            .follow_actions()

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
