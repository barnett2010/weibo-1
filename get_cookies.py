from selenium import webdriver
import time
import json

path = r'C:\Users\Administrator\Desktop\项目\chromedriver.exe'
browser = webdriver.Chrome(executable_path=path)
url = 'https://weibo.com/'
browser.get(url)
time.sleep(10)  #没有对验证码进行自动处理，所以在接下来的几秒内自己手动输入验证码
name_input = browser.find_element_by_id('loginname')
name_input.send_keys('xxx')
time.sleep(2)
password_input = browser.find_element_by_name('password')
password_input.send_keys('xxx')
time.sleep(2)
login_input = browser.find_elements_by_xpath('//div[@class="info_list login_btn"]/a/span')
login_input[0].click()
time.sleep(10)
dictCookies = browser.get_cookies()
jsonCookies = json.dumps(dictCookies)
with open("cookies_weibo.json", "w") as fp:
    fp.write(jsonCookies)
browser.quit()

