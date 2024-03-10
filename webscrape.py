#%%
import sys, os, uuid, time, shutil, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from fake_useragent import UserAgent

import google.generativeai as genai
from _secrets import API_KEYS


#%%
# PubMed Scraping
# Settings for scanning PubMed
TARGET_ROOT_URL = "https://pubmed.ncbi.nlm.nih.gov/"
SEARCH_TERM = "alpelisib Arginine"
WAIT_INDEFINITELY = False
GOOGLE_API_KEY = API_KEYS["Gemini"]
FIRST_N = 10

# %%
# Set up a session and configure browser
SESSION_ID = str(uuid.uuid4())
print(SESSION_ID)
DOWNLOAD_PATH = os.getcwd() + "\\temp\\" + SESSION_ID

chrome_options = Options()
ua = UserAgent()
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
driver.get(TARGET_ROOT_URL)
print("Connected to", driver.title)
driver.implicitly_wait(0.5)

text_box = driver.find_element(by=By.NAME, value="term")
submit_button = driver.find_element(by=By.CLASS_NAME, value="search-btn")

text_box.send_keys(SEARCH_TERM)
submit_button.click()

save_panel_btn = driver.find_element(by=By.ID, value="save-results-panel-trigger")
save_panel_btn.click()
driver.implicitly_wait(1)


results_selector = driver.find_element(By.NAME, "results-selection")
select = Select(results_selector)
select.select_by_index(1)

format_selector = driver.find_element(By.NAME, "results-format")
select = Select(format_selector)
select.select_by_index(1)

submit_button = driver.find_element(by=By.CLASS_NAME, value="action-panel-submit")
submit_button.click()

print("Download initiated.")
if WAIT_INDEFINITELY:
    input("Press Enter to continue...")
else:
    print("Waiting for download to complete...")
    time.sleep(10)

#%%
dat = None
downloaded_files = os.listdir(DOWNLOAD_PATH)
print(downloaded_files)

#%%
if len(downloaded_files) == 0:
    print("Nothing downloaded.")
    sys.exit()
else:
    print("Download completed.")
    driver.quit()
    file = downloaded_files[0]
    with open("temp" + "\\" + SESSION_ID + "\\" + file) as f:
        dat = f.read()
    shutil.rmtree("temp")

# %%
print(dat)


#%%
def select_string_with_substring(strings, substring):
    selected_strings = [s for s in strings if s.startswith(substring)]
    return selected_strings

#%%
datl = dat.split("\n")
datlf = select_string_with_substring(datl, "AB  - ")
#%%
in_prompt = [i[6:] for i in datlf[:FIRST_N]]
in_prompt = ", ".join(in_prompt)
in_prompt = "Summarize the following in context of " + SEARCH_TERM + ". Respond in pointers with details: \n" + in_prompt

# %%
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
# %%
print(SEARCH_TERM)
print('-'*20)
max_retries = 3
retry_count = 0
while retry_count < max_retries:
    try:
        response = model.generate_content(in_prompt)
        print(response.text)
        break
    except:
        retry_count += 1
        time.sleep(random.randint(5, 15))

# %%
