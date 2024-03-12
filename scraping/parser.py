from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone
import pandas as pd

def get_text(soup):
    """Get the text from the soup

    Args:
        soup (BeautifulSoup): The soup to get the text from

    Returns:
        str: The text from the soup
    """
    text = ""
    tags = ["h1", "h2", "h3", "h4", "h5", "p"]
    for element in soup.find_all(tags):  # Find all the <p> elements
        text += element.text + "\n\n"
    return text

def parse_gs_results(results):
    """
    Get SERPs from soup extracted from selenium driver and retrun a json
    """
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

def parse_pubmed_results(data):
    rows = []
    items = data.split("\n\n")
    for i in items:    
        row = dict()    
        i = i.replace("\n      ","")
        components = i.split("\n")
        for c in components:
            if c.startswith("PMID- "):
                row["PMID"] = c[6:]
            elif c.startswith("LID - ") and c.endswith("[doi]"):
                row["DoI"] = c[6:-6]
            elif c.startswith("TI  - "):
                row["Title"] = c[6:]
            elif c.startswith("AB  - "):
                row["Abstract"] = c[6:]
        rows.append(row)
    df =  pd.DataFrame(rows)
    df = df.dropna(inplace=False)
    return df

def parse_wiki(data):
    body_content = data
    soup = BeautifulSoup(body_content.get_attribute("innerHTML"), "html.parser")
    paragraphs = []
    for para in soup.find_all("p"):
        paragraphs.append(para.get_text())
    text = "".join(paragraphs)
    return(text)

def extract_paragraphs(data):
    soup = data
    paragraphs = []
    for para in soup.find_all("p"):
        paragraphs.append(para.get_text())
    text = "".join(paragraphs)
    return(text)