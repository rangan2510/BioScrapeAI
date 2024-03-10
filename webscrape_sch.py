#%%
import sys, os, uuid, time, shutil, random, re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#%%
def parse_results(results):
    parsed_res = []
    for r in results:
        r.get_attribute("innerHTML")
        soup = BeautifulSoup(r.get_attribute("innerHTML"), "html.parser")
        print(soup.div.text.split("-"))
        res = dict()
        res["Title"] = soup.h3.text
        res["Authors"] = soup.div.text.split("-")[0].replace("\xa0","")
        res["Publication"] = "".join(soup.div.text.split("-")[1:]).replace("\xa0","")
        try:
            res["Cites"] = re.search(r"Cited by \d*", soup.find("div", class_="gs_flb").get_text()).group().replace("Cited by ","")
        except:
            res["Cites"] = None
        res["Link"] = soup.a["href"]
        res["Snippet"] = soup.find("div", class_="gs_rs").get_text().replace("\n","")
        parsed_res.append(res)
    return parsed_res


#%%
# Google Scholar Scraping
# Settings for scanning GS
TARGET_ROOT_URL = "https://scholar.google.com/scholar?&q="
SEARCH_TERM = "Alpelisib Arginine"

# %%
# Set up a session and configure browser
SESSION_ID = str(uuid.uuid4())
print(SESSION_ID)
DOWNLOAD_PATH = os.getcwd() + "\\temp\\" + SESSION_ID

chrome_options = Options()
ua = UserAgent(browsers=['edge', 'chrome'])
user_agent = ua.random
print(user_agent)

chrome_options.add_argument("--headless=new")
chrome_options.add_argument(f'--user-agent={user_agent}')

chrome_options.add_experimental_option("prefs", {
  "download.default_directory": DOWNLOAD_PATH
  })

driver = webdriver.Chrome(options=chrome_options)

#%%
# begin session
TARGET_URL = TARGET_ROOT_URL + "+".join(SEARCH_TERM.split(" "))
driver.get(TARGET_URL)
print("Connected to", driver.title)
driver.implicitly_wait(0.5)
serp1 = driver.find_elements(by=By.CLASS_NAME, value="gs_ri")
driver.implicitly_wait(2)

json_resp = parse_results(serp1)
df = pd.DataFrame(json_resp)
df

#%%
TARGET_URL = TARGET_ROOT_URL + "+".join(SEARCH_TERM.split(" ")) + "&start=10"
driver.get(TARGET_URL)
print("Connected to", driver.title)
driver.implicitly_wait(0.5)
serp2 = driver.find_elements(by=By.CLASS_NAME, value="gs_ri")

json_resp = parse_results(serp2)
df = pd.DataFrame(json_resp)
df