#%%
import pandas as pd

#%%
def select_string_with_substring(strings, substring):
    selected_strings = [s for s in strings if s.startswith(substring)]
    return selected_strings


#%%
def pubmed2df(data):
    rows = []
    items = data.split("\n\n")
    for i in items:    
        row = dict()    
        i = i.replace("\n      ","")
        components = i.split("\n")
        for c in components:
            if c.startswith("PMID- "):
                row["pmid"] = c[6:]
            elif c.startswith("LID - ") and c.endswith("[doi]"):
                row["doi"] = c[6:-6]
            elif c.startswith("TI  - "):
                row["title"] = c[6:]
            elif c.startswith("AB  - "):
                row["abstract"] = c[6:]
        rows.append(row)
    df =  pd.DataFrame(rows)
    df = df.dropna(inplace=False)
    return df
# %%
