#%%
import sys, os, uuid, time, shutil, random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

from fake_useragent import UserAgent
import google.generativeai as genai

sys.path.append('../')
from _secrets import API_KEYS
from scraping.parser import parse_wiki


#%%
from bs4 import BeautifulSoup

# %%
def get_wiki(search_term, debug=False):
    TARGET_ROOT_URL = "https://www.wikipedia.org/"
    SEARCH_TERM = search_term
    GOOGLE_API_KEY = API_KEYS["Gemini"]

    SESSION_ID = str(uuid.uuid4())
    print("Session ID:\t", SESSION_ID)
    DOWNLOAD_PATH = os.getcwd() + "\\temp\\" + SESSION_ID

    ua = UserAgent(browsers=['edge', 'chrome'])
    user_agent = ua.random
    print("User agent:\t", user_agent)

    firefox_options = Options()
    if not debug:
        firefox_options.add_argument("-headless")
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", DOWNLOAD_PATH)
    # firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    driver = webdriver.Firefox(options=firefox_options)

    driver.get(TARGET_ROOT_URL)
    print("Connected to", driver.title)
    driver.implicitly_wait(1)
    
    text_box = driver.find_element(by=By.ID, value="searchInput")
    submit_button = driver.find_element(by=By.CLASS_NAME, value="pure-button.pure-button-primary-progressive")
    text_box.send_keys(SEARCH_TERM)
    submit_button.click()

    body_content = driver.find_element(by=By.ID, value="bodyContent")
    text = parse_wiki(body_content)

    in_prompt = "Summarize the following while preserving details as much as possible: \n" + text

    max_retries = 3
    retry_count = 0

    GOOGLE_API_KEY = API_KEYS["Gemini"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    print("Attempting to summarize...")
    while retry_count < max_retries:
        try:
            response = model.generate_content(in_prompt)
            summary_text = response.text
            break
        except Exception as e:
            retry_count += 1
            time.sleep(random.randint(5, 15))
            print(e)
            summary_text = "Failed to get a response." + str(e)

    print("Done.")
    return(text, summary_text)


#%%
# text, summary = get_wiki("Alpelisib")

#%%