#%%
import sys, os, uuid, time, shutil, random
from tqdm import tqdm, trange
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

from fake_useragent import UserAgent
import google.generativeai as genai

sys.path.append('../')
from _secrets import API_KEYS
from scraping.utils import select_string_with_substring
from scraping.parser import parse_pubmed_results


# %%
def get_pubmed(search_term, first_n=10, wait_for=30, debug=False):
    TARGET_ROOT_URL = "https://pubmed.ncbi.nlm.nih.gov/"
    SEARCH_TERM = search_term
    WAIT_INDEFINITELY = False # not implemented
    GOOGLE_API_KEY = API_KEYS["Gemini"]
    FIRST_N = first_n

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

    driver.get(TARGET_ROOT_URL)
    print("Connected to", driver.title)
    driver.implicitly_wait(1)

    text_box = driver.find_element(by=By.NAME, value="term")
    submit_button = driver.find_element(by=By.CLASS_NAME, value="search-btn")

    text_box.send_keys(SEARCH_TERM)
    submit_button.click()

    save_panel_btn = driver.find_element(by=By.ID, value="save-results-panel-trigger")
    save_panel_btn.click()
    driver.implicitly_wait(1)
    time.sleep(2)


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
        for _ in trange(wait_for):
            time.sleep(1)

    dat = None
    downloaded_files = os.listdir(DOWNLOAD_PATH)
    
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

    # print(dat)

    df = parse_pubmed_results(dat)
    print("Parsed results.")

    abstracts = df["Abstract"].to_list()
    in_prompt = ", ".join(abstracts[:FIRST_N])
    in_prompt = "Summarize the following in details: \n" + in_prompt

    max_retries = 3
    retry_count = 0
    GOOGLE_API_KEY = API_KEYS["Gemini"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    print("Attempting to summarize.")
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

    return(df, summary_text)

# %%
# df, summary = get_pubmed("Alpelisib", debug=True)
# print(df)
# print(summary)

#%%