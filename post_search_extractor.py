import time
from typing import Callable, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from post_extractor import PostExtractor
from post_desktop_extractor import PostDesktopExtractor
from post_mobile_extractor import PostMobileExtractor
from selenium_utils import SeleniumUtils
from utils.log_utils import logger
from utils.common_utils import CommonUtils
from post_model import Post
import json
from unidecode import unidecode

class PostElementIterator:
    def __init__(self, post_element_list: List[WebElement]):
        self.post_element_list = post_element_list
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.post_element_list):
            raise StopIteration

        post = self.post_element_list[self.index]
        self.index += 1
        return post

    def update(self, post_element_list: List[WebElement]):
        self.post_element_list = post_element_list

class PostMobileSearchExtractor:
    driver: WebDriver
    FACEBOOK_SEARCH_LINK: str = "https://m.facebook.com/search/posts?q="
    RECENT_POST_FILTER: str = "&filters=eyJyZWNlbnRfcG9zdHM6MCI6IntcIm5hbWVcIjpcInJlY2VudF9wb3N0c1wiLFwiYXJnc1wiOlwiXCJ9In0%3D"
    POST_CONTENT_XPATH: str = './/div[@data-gt=\'{"tn":"*s"}\']'
    POST_SHARE_CONTENT_XPATH: str = './/div[@data-gt=\'{"tn":"*s"}\']'

    BACK_NAVIGATION_BAR_XPATH: str = '//a[@data-sigil="MBackNavBarClick"]'
    POST_XPATH: str = "//div[contains(@class, 'async_like')]"
    POST_SHARE_XPATH: str = '//div[contains(@class, "async_like")]//div[contains(@class, "async_like")]'
    posts: List[Post] = []
    callback: Optional[Callable[[Post], None]] = None

    def __init__(self, driver: WebDriver, keyword: str, keyword_noparse: List, callback: Optional[Callable[[Post], None]] = None):
        self.url = f"{self.FACEBOOK_SEARCH_LINK}{keyword}{self.RECENT_POST_FILTER}"
        self.callback = callback
        self.driver = driver
        self.driver.get(self.url)
        self.driver.implicitly_wait(1000)
        self.keyword_noparse = keyword_noparse
        slept_time = CommonUtils.sleep_random_in_range(1, 5)
        logger.debug(f"Slept {slept_time}")

    def _get_current_post_element(self) -> Optional[WebElement]:
        try:
            self.driver.implicitly_wait(5)
            return self.driver.find_element(By.XPATH, self.POST_XPATH)
        except NoSuchElementException:
            logger.error(f"Not found {self.POST_XPATH}")
            return None
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
    def _get_post_share_element(self) -> Optional[WebElement]:
        try:
            self.driver.implicitly_wait(5)
            return self.driver.find_element(By.XPATH, self.POST_SHARE_XPATH)
        except NoSuchElementException:
            logger.error(f"Not found {self.POST_SHARE_XPATH}")
            return None
        except Exception as e:
            logger.error(e, exc_info=True)
            return None

    def _get_current_post_element_list(self) -> Tuple[List[WebElement], int]:
        post_element_list: List[WebElement] = []
        try:
            self.driver.implicitly_wait(5)
            post_element_list = self.driver.find_elements(By.XPATH, self.POST_XPATH)
            post_element_list_size = len(post_element_list)
            logger.debug(f"So bai post hien thi tren giao dien: {post_element_list_size}")
            return post_element_list, post_element_list_size
        except NoSuchElementException:
            logger.error(f"Not found {self.POST_XPATH}")
            return post_element_list, 0
        except Exception as e:
            logger.error(e, exc_info=True)
            return post_element_list, 0

    def unsigned_text(self, content : str):
        return unidecode(content).lower()

    def get_key_subkey(self, keyword_list_raw: str) -> List[str]:
        keyword_list_raw_dict = json.loads(keyword_list_raw)
        keyword_list = []
        subkey_list  = []
        # Lặp qua mỗi dict trong danh sách
        for item in keyword_list_raw_dict:
            item_key = {}
            # Lấy giá trị của key
            key = item['key']
            item_key['key'] = self.unsigned_text(key)
            # Lặp qua mỗi giá trị trong subKey
            for subkey in item['subKey']:
                subkey_list.append(self.unsigned_text(subkey))
                # Thêm từ khóa kết hợp vào danh sách keywords
            item_key['subkey'] = subkey_list
            keyword_list.append(item_key)

        return keyword_list

    def start(self) -> List[Post]:
        post_element_list, post_element_list_size = self._get_current_post_element_list()
        post_element_iterator = PostElementIterator(post_element_list=post_element_list)
        key_unsigned = self.get_key_subkey(self.keyword_noparse)
        while post_element_iterator.index < 20:
            try:
                post_element = next(post_element_iterator)
                self._enter_post(post_element)

                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                logger.debug(f"Slept {slept_time}")
                post_element = self._get_current_post_element()
                if post_element:
                    post_share_element = self._get_post_share_element()
                    isPostShare = True if post_share_element else False
                    post_extractor: PostMobileExtractor = PostMobileExtractor(driver=self.driver, post_element=post_element)
                    post = post_extractor.extract()
                    retry_time = 0
                    def retry_extract(post, retry_time):
                        while not post.is_valid():
                            post = post_extractor.extract()
                            if retry_time > 0:
                                logger.debug(f"Try to extract post {retry_time} times {str(post)}")
                                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                                logger.debug(f"Slept {slept_time}")
                            retry_time = retry_time + 1
                            if retry_time > 20:
                                logger.debug("Retried 20 times, skip post")
                                break
                        return
                    retry_extract(post, retry_time)
                    #---Quan--12/7/2023 2:48:00-- lọc những bài viết không liên quan đến từ khóa
                    def filter_post(post):
                        logger.debug("-----______----------")
                        contents_unsigned = self.unsigned_text(post.content)
                        for item_key in key_unsigned:
                            if item_key['key'] in contents_unsigned:
                                for sub_k in item_key['subkey']:
                                    if sub_k in contents_unsigned:
                                        self.posts.append(post)
                                        break
                    filter_post(post)
                    if isPostShare:
                        enter_post = self._enter_post_share(post_share_element)
                        slept_time = CommonUtils.sleep_random_in_range(1, 3)
                        logger.debug(f"Slept {slept_time}")
                        post_share_element = self._get_current_post_element()
                        slept_time = CommonUtils.sleep_random_in_range(1, 5)
                        logger.debug(f"Slept {slept_time}")
                        if post_share_element:
                            post_share_extractor: PostMobileExtractor = PostMobileExtractor(driver=self.driver, post_element=post_share_element)
                            post_share = post_share_extractor.extract()
                            retry_time = 0
                            retry_extract(post_share, retry_time)
                            #post.post_share = post_share
                            filter_post(post_share)
                            if enter_post is not None:
                                self._back()
                                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                                logger.debug(f"Slept {slept_time}")


                    # while not post.is_valid():
                    #     post = post_extractor.extract()
                    #     if retry_time > 0:
                    #         logger.debug(f"Try to extract post {retry_time} times {str(post)}")
                    #         slept_time = CommonUtils.sleep_random_in_range(1, 5)
                    #         logger.debug(f"Slept {slept_time}")
                    #     retry_time = retry_time + 1
                    #     if retry_time > 20:
                    #         logger.debug("Retried 20 times, skip post")
                    #         break
                    
                    if self.callback:
                        self.callback(post)

                self._back()
                #self._back()
                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                logger.debug(f"Slept {slept_time}")

                post_element_list, post_element_list_size = self._get_current_post_element_list()
                post_element_iterator.update(post_element_list=post_element_list)
            except StopIteration as e:
                logger.debug(f"Đã hết post của từ khóa")
                break
        return self.posts

    def _get_post_content_element(self, post_element: WebElement) -> WebElement:
        return post_element.find_element(by=By.XPATH, value=self.POST_CONTENT_XPATH)
            
    def _enter_post(self, post_element: WebElement):
        logger.info("Start")
        post_content_element = self._get_post_content_element(post_element=post_element)
        a_post_content_element = post_content_element.find_element(by=By.XPATH, value='.//a[@aria-label]')
        SeleniumUtils.click_element(driver=self.driver, element=a_post_content_element)
        logger.info(f"End")

    def _get_post_share_content_element(self, post_element: WebElement) -> WebElement:
        return post_element.find_element(by=By.XPATH, value=self.POST_SHARE_CONTENT_XPATH)

    def _enter_post_share(self, post_element: WebElement):
        logger.info("Start")
        try:
            #post_content_element = self._get_post_share_content_element(post_element=post_element)
            a_post_content_element = post_element.find_element(by=By.XPATH, value='.//div[@data-sigil="m-feed-voice-subtitle"]//a')
            SeleniumUtils.click_element(driver=self.driver, element=a_post_content_element)
            
        except NoSuchElementException:
            logger.error(f"Not found xpath enter post share")
            return None
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        logger.info(f"End")
        return 1

    def _get_back_navigation_bar_element(self) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value=self.BACK_NAVIGATION_BAR_XPATH)
        
    def _back(self):
        logger.info("Start")
        back_navigation_bar_element = self._get_back_navigation_bar_element()
        SeleniumUtils.click_element(driver=self.driver, element=back_navigation_bar_element)
        logger.info("End")


class PostDesktopSearchExtractor:
    driver: WebDriver
    FACEBOOK_SEARCH_LINK: str = "https://www.facebook.com/search/posts?q="
    RECENT_POST_FILTER: str = "&filters=eyJyZWNlbnRfcG9zdHM6MCI6IntcIm5hbWVcIjpcInJlY2VudF9wb3N0c1wiLFwiYXJnc1wiOlwiXCJ9In0%3D"
    POST_CONTENT_XPATH: str = './/div[@data-ad-preview or contains(@style, "background-image")]'
    POST_XPATH: str = './/div[@aria-posinset]'
    callback: Optional[Callable[[Post], None]] = None

    def __init__(self, driver: WebDriver, keyword: str, callback: Optional[Callable[[Post], None]] = None):
        self.url = f"{self.FACEBOOK_SEARCH_LINK}{keyword}{self.RECENT_POST_FILTER}"
        self.callback = callback
        self.driver = driver
        self.driver.get(self.url)
        self.driver.implicitly_wait(1000)
        slept_time = CommonUtils.sleep_random_in_range(1, 5)
        logger.debug(f"Slept {slept_time}")

    def _get_current_post_element_list(self) -> Tuple[List[WebElement], int]:
        post_element_list: List[WebElement] = []
        try:
            self.driver.implicitly_wait(5)
            post_element_list = self.driver.find_elements(By.XPATH, self.POST_XPATH)
            post_element_list_size = len(post_element_list)
            logger.debug(f"So bai post hien thi tren giao dien: {post_element_list_size}")
            return post_element_list, post_element_list_size
        except NoSuchElementException:
            logger.error(f"Not found {self.POST_XPATH}")
            return post_element_list, 0
        except Exception as e:
            logger.error(e, exc_info=True)
            return post_element_list, 0



    def start(self):
        post_element_list, post_element_list_size = self._get_current_post_element_list()
        post_element_iterator = PostElementIterator(post_element_list=post_element_list)
        while post_element_iterator.index < 20:
            try:
                post_element = next(post_element_iterator)
                self._enter_post(post_element)
                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                logger.debug(f"Slept {slept_time}")
                if post_element:
                    post_desktop_extractor: PostDesktopExtractor = PostDesktopExtractor(driver=self.driver, post_element=post_element)
                    post = post_desktop_extractor.extract()
                    # retry_time = 0
                    # while not post.is_valid():
                    #     post = post_desktop_extractor.extract()
                    #     if retry_time > 0:
                    #         logger.debug(f"Try to extract post {retry_time} times {str(post)}")
                    #         slept_time = CommonUtils.sleep_random_in_range(1, 5)
                    #         logger.debug(f"Slept {slept_time}")
                    #     retry_time = retry_time + 1
                    
                    if self.callback:
                        self.callback(post)

                slept_time = CommonUtils.sleep_random_in_range(1, 5)
                logger.debug(f"Slept {slept_time}")

                post_element_list, post_element_list_size = self._get_current_post_element_list()
                post_element_iterator.update(post_element_list=post_element_list)
            except StopIteration as e:
                logger.debug(f"Đã hết post của từ khóa")
                return

    def _get_post_content_element(self, post_element: WebElement) -> WebElement:
        return post_element.find_element(by=By.XPATH, value=self.POST_CONTENT_XPATH)
            
    def _enter_post(self, post_element: WebElement):
        logger.info("Start")
        post_content_element = self._get_post_content_element(post_element=post_element)
        SeleniumUtils.click_element(driver=self.driver, element=post_content_element)
        logger.info(f"End")