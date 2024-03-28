#%%
import os, uuid, re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# %%
def extract_paragraphs(data):
    soup = data
    paragraphs = []
    for para in soup.find_all("p"):
        paragraphs.append(para.get_text())
    text = "".join(paragraphs)
    return(text)

def parse_gs_results(results):
    parsed_res = []
    for r in results:
        r.get_attribute("innerHTML")
        soup = BeautifulSoup(r.get_attribute("innerHTML"), "html.parser")
        res = dict()
        res["Title"] = soup.h3.text.replace("[HTML]","")
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

    firefox_options = Options()
    if not debug:
        firefox_options.add_argument("-headless")
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", DOWNLOAD_PATH)
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
    df.reset_index()
    texts = []
    for idx, row in df.iterrows():
        link = row["Link"]
        try:
            print(idx, ": attempting connection to", link)
            driver.get(link)
            # Get the HTML content directly from the browser's DOM
            page_source = driver.execute_script("return document.body.outerHTML;")
            soup = BeautifulSoup(page_source, "html.parser")
            text = extract_paragraphs(soup)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)
            print("Connection succeeded.")
        except:
            text = ""
            print("Connection failed.")
        texts.append(text)

    df["Text"] = texts


    driver.quit()
    return df

#%%
df = get_gs("alpelisib")

#%%