#%%
import pandas as pd
import json

#%%
# Read local target list
target_df = pd.read_excel("./input/HSMD-drugs.xlsx")

# File specific operations
# Modify as needed
target_list = target_df.Drugs.to_list()
target_list = [i.split("/") for i in target_list]
target_list = [x.lower() for xs in target_list for x in xs]
target_list = list(set(target_list))

#%%
# look up local db
synonyms = pd.read_csv("./data/synonyms.csv")
synonyms.fillna("", inplace=True)

filtered_df = pd.DataFrame()
query = []
for drug in target_list:
    temp_df = synonyms[synonyms['Synonyms'].str.contains(drug, case=False)]
    temp_df["Query"] = [drug]*len(temp_df)
    filtered_df = pd.concat([filtered_df, temp_df])

hits_df = filtered_df.drop_duplicates()

#%%
with open("./data/localdb.json","r") as ldb:
    full_db = json.load(ldb)

#%%
drug_dicts = []
hits = hits_df["DrugBank ID"].to_list()
for obj in full_db:
    # name
    objname = obj['name']
    filetype = obj['@type']

    # drugbank-id
    try:
        k,v = obj['drugbank-id'][0].items()
        fileid = v[1]
    except:
        fileid = obj['drugbank-id']['#text']
    
    # cas
    try:
        cas = obj["cas-number"]
    except:
        cas = ""
    
    # atc
    try:
        atc = obj["atc-codes"]["atc-code"]
        if type(atc) == dict:
            atc = atc["@code"]
        if type(atc) == list:
            for atc_i in atc:
                atc_k = atc_i["@code"]
            atc = atc[0]["@code"]
    except:
        if atc is not None:
            atc = obj["atc-codes"]
        else:
            atc = ""

    #rxcui        
    try:        
        ext_ids = obj['external-identifiers']['external-identifier']
        for item in ext_ids:
            if(item['resource'] == 'RxCUI'):
                rxcui = item['identifier']
    except:
        rxcui=""

        
    #Unii
    try:
        unii = obj['unii']
    except:
        unii = ""
    

    #uniprotkb
    try:        
        ext_ids = obj['external-identifiers']['external-identifier']
        for item in ext_ids:
            if(item['resource'] == 'UniProtKB'):
                uniprotkb = item['identifier']
    except:
        uniprotkb=""


    drug_row = {
        'name': objname,
        'drugbank-id': fileid,
        'type':filetype,
        'atc':atc,
        'cas':cas,
        'rxcui':rxcui,
        'unii':unii,
        'uniprot_kb':uniprotkb,
        "description" : obj["description"],
        "synthesis-reference" : obj["synthesis-reference"],
        "indication" : obj["indication"],
        "pharmacodynamics" : obj["pharmacodynamics"],
        "mechanism-of-action" : obj["mechanism-of-action"],
        "toxicity" : obj["toxicity"],
        "metabolism" : obj["metabolism"],
        "absorption" : obj["absorption"],
        "half-life" : obj["half-life"],
        "protein-binding" : obj["protein-binding"],
        "route-of-elimination" : obj["route-of-elimination"],
        "volume-of-distribution" : obj["volume-of-distribution"],
        "clearance" : obj["clearance"]
    }
    if fileid in hits:
        drug_dicts.append(drug_row)
    
drugs_df = pd.DataFrame(drug_dicts)
drugs_df.to_excel("./out/drugbank/drugbank.xlsx")
