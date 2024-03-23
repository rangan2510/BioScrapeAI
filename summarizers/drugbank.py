#%%
import os, time, random
from tqdm.auto import tqdm
import pandas as pd
import google.generativeai as genai
genai.configure(api_key="AIzaSyAyFvc6BYD0Tl7-PWLskNLjFEHC6P3RsxU")
model = genai.GenerativeModel('gemini-pro')

#%%
source_path = "../out/drugbank/drugbank.xlsx"
drugbank_df = pd.read_excel(source_path)
drugbank_df = drugbank_df.iloc[: , 1:]

#%%
for col in drugbank_df.columns:
        drugbank_df.fillna({col:""}, inplace=True)

list_of_cols= ['description','indication','pharmacodynamics','mechanism-of-action','toxicity','metabolism','absorption',
               'half-life','route-of-elimination']

#%%
save_path = "../out/drugbank/summary/"

for index, row in drugbank_df.iterrows():
    drug_name = row['name']
    #row_context = ""
    for column in list_of_cols:
        info= str(row[column])
        in_prompt = "Write a single paragraph about " + column + " of  " + drug_name + "based on the following information for breast cancer:\n" + info

        max_retries = 3
        retry_count = 0

        print(index+1, drug_name, column, ": attempting to summarize...")
        while retry_count < max_retries:
            try:
                response = model.generate_content(in_prompt)
                summary_text = response.text
                print(summary_text)
                filename = drug_name + "_" + column + ".txt"
                print("saving to", save_path + filename)
                with open(save_path + filename, "w") as fp:
                    fp.write(summary_text)
                time.sleep(random.randint(1,5))
                break
            except Exception as e:
                retry_count += 1
                print("ERROR:",e)
                wait_timer = random.randint(45, 120)
                print("Waiting for", wait_timer)
                time.sleep(wait_timer)
        print("Done.")
    time.sleep(random.randint(5,10))
    

#%%
