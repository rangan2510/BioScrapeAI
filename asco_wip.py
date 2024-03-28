#%%
import os, uuid, re, time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

debug = True
# %%
# Gathering all links
TARGET_ROOT_URL = "https://society.asco.org/practice-patients/guidelines/breast-cancer"

ua = UserAgent(browsers=['edge', 'chrome'])
user_agent = ua.random
print("User agent:\t", user_agent)

firefox_options = Options()
if not debug:
    firefox_options.add_argument("-headless")
firefox_options.set_preference("browser.download.folderList", 2)
firefox_options.set_preference("browser.download.manager.showWhenStarting", False)

driver = webdriver.Firefox(options=firefox_options)

# begin session
driver.get(TARGET_ROOT_URL)
print("Connected to", driver.title)
driver.implicitly_wait(0.5)
driver.find_element(by=By.CLASS_NAME, value="onetrust-close-btn-handler.onetrust-close-btn-ui.banner-close-button.ot-close-icon").click()

#%%
urls = []
links = driver.find_elements(by=By.CLASS_NAME, value="guideline-load-link.active.guideline-load-link-processed")
driver.implicitly_wait(2)
time.sleep(2)
for i in links:
    urls.append(i.get_attribute("href"))
# %%

page_2_btn = driver.find_element(by=By.CLASS_NAME, value="pager-item.active.odd")
page_2_btn.click()
time.sleep(5)
links = driver.find_elements(by=By.CLASS_NAME, value="guideline-load-link.active.guideline-load-link-processed")
for i in links:
    urls.append(i.get_attribute("href"))

page_3_btn = driver.find_element(by=By.CLASS_NAME, value="pager-next.active.even.last")
page_3_btn.click()
time.sleep(5)
links = driver.find_elements(by=By.CLASS_NAME, value="guideline-load-link.active.guideline-load-link-processed")
for i in links:
    urls.append(i.get_attribute("href"))

driver.quit()

#%%
print(urls)
#%%

#%%
#put this in a loop
driver = webdriver.Firefox(options=firefox_options)
driver.get(urls[0])
title = driver.find_element(by=By.CLASS_NAME, value="node-title")
title = title.text

content = driver.find_element(by=By.CLASS_NAME, value="node-content")
content = content.text
driver.quit()

#%%
