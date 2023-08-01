import datetime
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from post_extractor import PostExtractor
from utils.datetime_utils import DatetimeUtils
from utils.log_utils import logger
from utils.string_utils import StringUtils
import json
import re
import time
import traceback
from post_model import Post
from selenium_utils import SeleniumUtils

class PostDesktopExtractor(PostExtractor):
    POST_AUTHOR_XPATH: str = './/a[not(contains(@href, "group")) and not(@href="#")]'
    def __init__(self, post_element: WebElement, driver: WebDriver):
        super().__init__(post_element=post_element, driver=driver)
    
    def _get_post_author_element(self, parent_element: Optional[WebElement] = None) -> Optional[WebElement]:
        try:
            self.driver.implicitly_wait(1)
            parent_element = parent_element if parent_element else self.post_element
            return parent_element.find_element(by=By.XPATH, value=self.POST_AUTHOR_XPATH)
        except NoSuchElementException as e:
            logger.error(f"Not found {self.POST_AUTHOR_XPATH}")
            return None
        except Exception as e:
            logger.error(e, exc_info=True)
            return None


    
    def extract_post_author(self):
        logger.info("Start")
        post_author: str = ''
        post_author_element = self._get_post_author_element()
        if post_author_element:
            post_author = post_author_element.get_attribute("aria-lable")
            logger.info("End")
        return post_author
    
    def extract_post_author_link(self) -> str:
        logger.info("Start")
        post_author_url: str = ''
        post_author_element = self._get_post_author_element()
        if post_author_element:
            post_author_url = post_author_element.get_attribute("href") + post_author_element.get_attribute("outerHTML")
            logger.info("End")
        return post_author_url
        

    
    def extract_post_author_avatar_link(self):
        pass

    
    def extract_post_time(self):
        pass

    
    def extract_post_content(self):
        pass

    
    def extract_post_link(self):
        pass

    
    def extract_post_id(self):
        pass

    
    def extract_post_photos(self):
        pass

    
    def extract_post_comments(self):
        pass


