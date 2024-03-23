#%%
from pymed import PubMed
from tqdm.auto import tqdm
import pandas as pd
import time, random

#%%
pubmed = PubMed()
#%%

df = pd.read_excel("HSMD-drugs.xlsx")
df
#%%
base_path = "./out/pubmed/"
queries = []
for idx, row in df.iterrows():
    query = str(row["Drugs"]).replace("/"," ").lower() + " " + str(row["Gene"]).replace("-","")
    queries.append(query)
queries = list(set(queries))

#%%
data = []
for q in tqdm(queries):
    time.sleep(random.randint(1,5))
    results = pubmed.query(q, max_results=50)
    for article in results:
        article_id = article.pubmed_id
        title = article.title
        publication_date = article.publication_date
        abstract = article.abstract
        print(
            f'{title}\n{abstract}\n'
        )
        data.append([article_id, publication_date, title, abstract, q])
# %%
results_df = pd.DataFrame(data, columns = ['ids', 'date', 'title', 'abstract', 'query'])
results_df.to_excel(base_path + "drug_target_pubmed.xlsx")
