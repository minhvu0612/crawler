import time
from typing import List
import config
import threading
import traceback
import crawler_utils
from post_model import Post
from post_search_extractor import PostMobileSearchExtractor
from utils.log_utils import logger
from browser import WebBrowser
from account_utils import * #get_cookie_from_account_fb, update_account_to_local_json_file



class CrawlerThread(threading.Thread):
    def __init__(self, account, keywords: List[str], addition_data, keyword_noparse):
        threading.Thread.__init__(self)
        self.account = account
        self.keywords = keywords
        self.thread_name = "Thread_" + account.username
        self.is_active = False
        self.web_browser = None
        self.work_thread = None
        self.bCheckout = False
        array_data = addition_data.split("+")
        if len(array_data) > 2:
            self.proxy = addition_data.split("+")[2]
        else:
            self.proxy = None
        self.keyword_noparse = keyword_noparse
        
    def run(self):
        print("Start clawer thread")
        try:
            is_login = self.login() #mở cmt dòng này nếu login bằng cokie và 2fa
            #is_login = self.login_with_userpass() #mở cmt dòng này nếu chỉ login bằng user, pass
            if is_login == 1:
                print("in duoc -----------")
                self.work()
        except Exception as ex:
            print(traceback.format_exc())
            print("Exception: run: " + str(ex))

    # [QUAN : 14/07/2023] -- Hàm login bằng user với pass 
    def login_with_userpass(self):
        self.web_browser = WebBrowser(proxy=self.account.proxy)
        self.web_browser.get_url(url=config.url_facebook)
        self.web_browser.login(self.account.username, self.account.password)
        time.sleep(config.time_wait_after_login_fb)
        if check_login(self.web_browser) == False:
            return 0
        elif check_nick_die(self.web_browser) == False:
            return 0
        self.is_active = True
        return 1

    def login(self):
        if not self.account.has_cookies():
            self.account.cookies = get_cookie_from_account_fb(account=self.account)

            update_account_to_local_json_file(account=self.account, file_path=config.account_path)
        time.sleep(2)

        print("Login accountFB: " + self.account.username)
        self.web_browser = WebBrowser(proxy=self.proxy)
        self.web_browser.get_url(url=config.url_facebook)
        result = self.web_browser.login_fb_with_cookie(self.account.get_cookies())
        # HoangLM: sua o day
        # result = self.web_browser.submit_2fakey_to_fb(297327)
        print("aaaa:", result)
        if result == 1:
            self.is_active = True
            return 1
        return 0

    def re_login(self):
        web_browser = WebBrowser(proxy=self.proxy)
        web_browser.get_url(url=config.url_facebook)
        web_browser.login_fb_with_cookie(cookie=self.account.get_cookies())
        return web_browser

    def on_post_available_callback(self, post: Post):
        with open("result.txt", "a", encoding="utf-8") as file:
            file.write(f"{str(post)}\n")
            # NguyenNH: in màu cho dễ debug
            if post.is_valid:
                file.write(f"🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷🇧🇷\n")
            else:
                file.write(f"🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈\n")

    def work(self):
        print("chuan bi in")
        print(self.keywords)
        while self.is_active:
            for keyword in self.keywords:
                post_mobile_search_extractor: PostMobileSearchExtractor = PostMobileSearchExtractor(driver=self.web_browser.driver, keyword=keyword, keyword_noparse=self.keyword_noparse, callback=self.on_post_available_callback)
                posts = post_mobile_search_extractor.start()
                logger.info(f"Send {len(posts)} to kafka")
                crawler_utils.push_kafka(posts=posts, comments=None)
            if self.bCheckout:
                break
            time_sleep = 3 * 3600
            print(f"Dang sleep {time_sleep}")
            time.sleep(time_sleep)
            print("Da xong 1 lan lam viec cua 1 tai khoan")

    def work_after_get_list_post(self, status_crawl, keyword):
        if status_crawl == config.crawl_complete_one_run:
            print("Hoan thanh lay tat ca bai viet cua tu khoa: " + str(keyword))
            pass
        elif status_crawl == config.crawl_re_login:
            print("Dang nhap lai")
            self.web_browser.driver.quit()
            self.web_browser = None
            self.web_browser = self.re_login()
            time.sleep(5)
        elif status_crawl == config.crawl_stop:
            print("Stop chuong trinh")
            self.web_browser.driver.quit()
            time.sleep(5)
            self.bCheckout = True
