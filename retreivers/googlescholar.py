#%%
import sys, os, uuid
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime

sys.path.append('../')
from scraping.parser import get_text
from scraping.parser import parse_gs_results
from scraping.utils import aware_utcnow

# %%
def get_gs(search_term, debug=False):
    TARGET_ROOT_URL = "https://scholar.google.com/scholar?&q="
    SEARCH_TERM = search_term

    # Set up a session and configure browser
    SESSION_ID = str(uuid.uuid4())
    print("Session ID:\t", SESSION_ID)
    DOWNLOAD_PATH = os.getcwd() + "\\temp\\" + SESSION_ID

    
    ua = UserAgent(browsers=['edge', 'chrome'])
    user_agent = ua.random
    print("User agent:\t", user_agent)

    # chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument(f'--user-agent={user_agent}')
    # chrome_options.add_experimental_option("prefs", {
    # "download.default_directory": DOWNLOAD_PATH
    # })
    # driver = webdriver.Chrome(options=chrome_options)

    firefox_options = Options()
    if not debug:
        firefox_options.add_argument("-headless")
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", DOWNLOAD_PATH)
    # firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    driver = webdriver.Firefox(options=firefox_options)

    # begin session
    TARGET_URL = TARGET_ROOT_URL + "+".join(SEARCH_TERM.split(" "))
    driver.get(TARGET_URL)
    print("Connected to", driver.title, "1/2")
    driver.implicitly_wait(0.5)
    serp1 = driver.find_elements(by=By.CLASS_NAME, value="gs_ri")
    driver.implicitly_wait(2)

    json_resp = parse_gs_results(serp1)
    df1 = pd.DataFrame(json_resp)

    TARGET_URL = TARGET_ROOT_URL + "+".join(SEARCH_TERM.split(" ")) + "&start=10"
    driver.get(TARGET_URL)
    print("Connected to", driver.title, "2/2")
    driver.implicitly_wait(0.5)
    serp2 = driver.find_elements(by=By.CLASS_NAME, value="gs_ri")

    json_resp = parse_gs_results(serp2)
    df2 = pd.DataFrame(json_resp)

    df = pd.concat([df1, df2])
    texts = []
    timestamps = []
    for idx, row in df.iterrows():
        link = row["Link"]
        try:
            print("Attempting connection to", link)
            driver.get(link)
            # Get the HTML content directly from the browser's DOM
            page_source = driver.execute_script("return document.body.outerHTML;")
            soup = BeautifulSoup(page_source, "html.parser")
            text = get_text(soup)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            print("Connection succeeded.")
        except:
            text = ""
            print("Connection failed.")
        texts.append(text)
        timestamps.append(aware_utcnow())
    df["Text"] = texts
    df["Accessed on"] = timestamps

    driver.quit()
    return df

#%%
# df = get_gs("Alpelisib", debug=True)

#%%