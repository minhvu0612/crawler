from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import logging

chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--incognito')
# chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    
service = Service(executable_path = '/usr/bin/chromedriver')
driver = webdriver.Chrome(options = chrome_options, service = service)
cookie = "Cookie: fr=04JYGh7uf8evp2VsV.AWU_fzJiT3cXowOoWa4eeII7b5U.BkyyFt.YY.AAA.0.0.BkyyF7.AWVaq9iunCo; sb=bSHLZDVlUatH7o8xD_67ygbR; datr=bSHLZO0pkCjPw6LK39ghAV5q; wd=1848x933; c_user=100087189767077; xs=35%3A5lg1HXsTtAiUzg%3A2%3A1691033977%3A-1%3A5820"

check_login = 0

def login_fb_with_cookie(cookie):
    try:
        driver.get("https://m.facebook.com")
        logging.info("Get fb success.")
        time.sleep(3)
        script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); ' \
                 'for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[' \
                 'i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ' \
                 '";domain=.facebook.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + ' \
                 'expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = ' \
                 'parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' \
                 + cookie + '"); location.href = "https://facebook.com"; })(); '
        driver.execute_script(script)
        logging.info("Login fb success.")
        return 1
    except Exception as e:
        logging.error("--Exception: " + e)
        return 0

def check_handle_login(check_login, cookie):
    if check_login:
        return check_login
    else:
        check_login = login_fb_with_cookie(cookie)
        return check_login

def get_content_fb():
    content = driver.find_element(by = By.CLASS_NAME, value = "x1lliihq")
    print(content)
    logging.info("--Content: " + str(content.text))

def fb_auto_liker():
    pass

def fb_auto_cmt():
    try:
        postURL = r"https://m.facebook.com/story.php?story_fbid=pfbid02f1PBwgPrRQAEQgKWbE9YHpmMK2cJxLprooHCbKL9w96ZRsAYXyr8W5RewkZaERZsl&id=100064714356916&eav=AfbMYYQTmsxs4F0CmnnpOIlHftljOT7LmahkAR_jFDrv5qs50_THby3nbKXVvG2APhU&m_entstream_source=feed_mobile&anchor_composer=false&paipv=0"
        driver.get(postURL)
        time.sleep(3)
        commentBox = driver.find_element(By.ID, value="composerInput")
        commentBox.send_keys("botCmnt")
        time.sleep(1)
        sendButton = driver.find_element(by=By.TAG_NAME, value="button")
        sendButton.click()
        print(sendButton)
    except Exception as e:
        logging.error("--Exception: " + str(e))
    
if __name__ == "__main__":
    check_handle_login(check_login, cookie)
    fb_auto_cmt()