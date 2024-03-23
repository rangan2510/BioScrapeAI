#%%
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
from wikipyedia_md import articles_to_markdown

#%%
def get_wiki(search_term, save_path, debug=False):
    TARGET_ROOT_URL = "https://www.wikipedia.org/"
    SEARCH_TERM = search_term

    ua = UserAgent(browsers=['edge', 'chrome'])
    user_agent = ua.random
    print("User agent:\t", user_agent)

    firefox_options = Options()
    if not debug:
        firefox_options.add_argument("-headless")
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    driver = webdriver.Firefox(options=firefox_options)

    driver.get(TARGET_ROOT_URL)
    print("Connected to", driver.title)
    driver.implicitly_wait(1)
    
    text_box = driver.find_element(by=By.ID, value="searchInput")
    submit_button = driver.find_element(by=By.CLASS_NAME, value="pure-button.pure-button-primary-progressive")
    text_box.send_keys(SEARCH_TERM)
    submit_button.click()

    url = driver.current_url
    articles_to_markdown([url], output_dir=save_path) 
    print("Done.")
    driver.quit()
    return

#%%
# Read local target list
target_df = pd.read_excel("./input/HSMD-drugs.xlsx")

# File specific operations
# Modify as needed
target_list = target_df.Drugs.to_list()
target_list = [i.split("/") for i in target_list]
target_list = [x.lower() for xs in target_list for x in xs]
target_list = list(set(target_list))

# %%
base_path = "./out/wiki"
target_list.sort()

#%%
# wikipedia 2 markdown dump
for idx, item in enumerate(target_list):
    print(idx+1,"/",len(target_list), "Processing",item,"...")
    get_wiki(item, base_path, debug=False)

# %%
