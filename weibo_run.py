from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import pymongo
from lxml import etree
from 项目.微博爬取.config import *

#需配置mongodb
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
chrome_options = Options()
chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面
chrome_options.add_argument("--window-size=1366,768")  # 设置浏览器分辨率（窗口大小）
chrome_options.add_argument('--start-maximized')    # 最大化运行（全屏窗口）,不设置，取元素会报错
chrome_options.add_argument('--blink-settings=imagesEnabled=false')   # 不加载图片, 提升速度
browser = webdriver.Chrome(executable_path="C:/Users/Administrator/Desktop/项目/chromedriver.exe",
                               chrome_options=chrome_options)

def cookies_get(url):
    browser.get(url)
    # 删除第一次登录是储存到本地的cookie
    browser.delete_all_cookies()
    # 读取登录时储存到本地的cookie，再次访问免登录
    with open("cookies_weibo.json", "r", encoding="utf8") as fp:
        ListCookies = json.loads(fp.read())
    for cookie in ListCookies:
        browser.add_cookie({
            'domain': '.weibo.com',
            'name': cookie['name'],
            'value': cookie['value'],
            'path': '/',
            'expires': None
        })

def data_get(url):
    browser.get(url)
    time.sleep(7)
    sreach_windows = browser.current_window_handle  # 输出当前窗口句柄
    all_handles = browser.window_handles   # 获取当前窗口句柄集合（列表类型）
    for handle in all_handles:
        if handle == sreach_windows:
            browser.switch_to.window(handle)
            time.sleep(1)
            num = 0
            page_list = 1
            while True:
                if num == 2:  # 只设置了两页
                    browser.close()
                    browser.quit()
                    break
                else:
                    if num == 0:
                        while page_list < 30:
                            one_page(page_list)
                            page_list += 1
                            if page_list == 11:
                                page_list += 2
                    else:
                        while page_list < 19:
                            one_page(page_list)
                            page_list += 1
                            if page_list == 11:
                                page_list += 2
                    pages_list = browser.find_element_by_link_text('下一页')
                    pages_list.click()
                    time.sleep(1)
                    page_list = 1
                    num = num + 1

def one_data_format():
    name_list = browser.find_element_by_xpath(
        '//*[@id="Pl_Official_WeiboDetail__72"]/div/div/div/div[5]/div/div[3]/div[2]/div/div[12]/div[2]/div[1]/a[1]')
    name_list.click()
    time.sleep(1)
    data_write()

def two_data_format(page_list):
    xpath_list = '//*[@id="Pl_Official_WeiboDetail__72"]/div/div/div/div[5]/div/div[3]/div[2]/div/div[' + str(page_list) + ']/div[2]/div[1]/a[1]'
    name_list = browser.find_element_by_xpath(xpath_list)
    name_list.click()
    time.sleep(1)
    data_write()

def data_write():
    sreach_windows = browser.current_window_handle
    all_handles = browser.window_handles
    for handle in all_handles:
        if handle != sreach_windows:
            browser.switch_to.window(handle)
            time.sleep(1)
            guest_tree = etree.HTML(browser.page_source)
            gz_name = browser.find_element_by_xpath('//*[@id="Pl_Official_Headerv6__1"]/div[1]/div/div[2]/div[2]/h1')
            gz_count = guest_tree.xpath('//td[@class="S_line1"][1]/a/strong//text()')
            gz_count_write = "".join(gz_count)
            fs_count = guest_tree.xpath('//td[@class="S_line1"][2]/a/strong//text()')
            fs_count_write = "".join(fs_count)
            wb_count = guest_tree.xpath('//td[@class="S_line1"][3]/a/strong//text()')
            wb_count_write = "".join(wb_count)
            product = {
                '昵称' : gz_name.text,
                '关注' : gz_count_write,
                '粉丝' : fs_count_write,
                '微博' : wb_count_write
            }
            save_to_mongo(product)
            browser.close()
    browser.switch_to_window(sreach_windows)

def one_page(page_list):
    if page_list == 11:
        one_data_format()
    else:
        two_data_format(page_list)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功',result)
    except Exception:
        print('存储到MONGODB失败', result)

def main():
    url = 'https://weibo.com/1776448504/HzbwL33fT?type=repost#_rnd1569066433734'
    cookies_get(url)
    data_get(url)

if __name__ == '__main__':
    main()

