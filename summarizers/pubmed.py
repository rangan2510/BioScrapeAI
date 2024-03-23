#%%
import time, random
import pandas as pd
from tqdm.auto import tqdm
import google.generativeai as genai

genai.configure(api_key="AIzaSyAyFvc6BYD0Tl7-PWLskNLjFEHC6P3RsxU")
model = genai.GenerativeModel('gemini-pro')
df = pd.read_excel(r"..\out\pubmed\drug_target_pubmed.xlsx")

#%%
summarized = []
for idx, row in tqdm(df.iterrows(), total=len(df)):
    title = row['title']
    abstract = row['abstract']
    if abstract!=None:
        in_prompt = "Given the following title and abstract, write a short but detailed single paragraph summary. Focus on the drug, it's target and the outcome. Do not mention \"This study\" in the response, simply talk in geenral. \nTitle: " + title + "\nAbstract:" + abstract
        ids = row["ids"].replace("\n",",")
        date = row['date'].strftime("%Y %B %d")

        max_retries = 3
        retry_count = 0

        model = genai.GenerativeModel('gemini-pro')

        print(idx+1, "Attempting to summarize...")
        while retry_count < max_retries:
            try:
                response = model.generate_content(in_prompt)
                summary_text = response.text
                break
            except Exception as e:
                retry_count += 1
                time.sleep(random.randint(1, 5))
                print(e)
                summary_text = ""

        summarized.append([ids, date, title, abstract, summary_text, row['query']])
        print("Done.")

# %%
summarized_df = pd.DataFrame(summarized, columns = ['ids', 'date', 'title', 'abstract', 'summary_text', 'query'])
summarized_df.to_csv("../out/pubmed/drug_target_pubmed.tsv", sep="\t")