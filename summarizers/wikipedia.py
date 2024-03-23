#%%
import os, time, random
import pandas as pd
from tqdm.auto import tqdm

import google.generativeai as genai
model = genai.GenerativeModel('gemini-pro')
genai.configure(api_key="AIzaSyAyFvc6BYD0Tl7-PWLskNLjFEHC6P3RsxU")
# %%
base_path = "..\\out\\wiki"
selected_files = []
for root, dirs, files in os.walk(base_path):
    for file in files:
        selected_files.append(os.path.join(root, file))
selected_files.sort()

#%%
for i, path in enumerate(selected_files):

    filename = path.split("\\")[-1]

    with open(path, "r") as fp:
        data = fp.read()

    in_prompt = "Summarize the following content in a paragraph while preserving details as much as possible. \
        Do not talk about any studies in particular, mention the facts in general. Here is the content: \n" + data

    max_retries = 5
    retry_count = 0

    print(i+1, ": attempting to summarize...")
    while retry_count < max_retries:
        try:
            response = model.generate_content(in_prompt)
            summary_text = response.text
            break
        except Exception as e:
            retry_count += 1
            print("ERROR:",e)
            wait_timer = random.randint(45, 120)
            print("Waiting for", wait_timer)
            time.sleep(wait_timer)

    print("Done.")
    time.sleep(random.randint(1,5))

    with open(base_path + "\\summary\\" + filename, "w+") as fp:
        fp.write(summary_text)

# %%
