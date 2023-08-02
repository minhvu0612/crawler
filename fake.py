from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time

chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 2})
    
service = Service(executable_path='/usr/bin/chromedriver')

if __name__ == "__main__":
    #chrome_options = set_chrome_options()
    driver = webdriver.Chrome(options=chrome_options, service = service)
    # Do stuff with your driver
    driver.get("https://www.google.com.vn/?hl=vi")
    time.sleep(3)
    #driver.close()
