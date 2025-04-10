import pandas as pd
import spacy
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

# import
path_import='./Data/Data_raw/file_2.csv'
path_export='./Data/Data_result/file_2_reUSCS.csv'

f2=pd.read_csv(path_import)
f2.dropna(subset=['Lithology'], inplace=True)

# mapping dict
uscs_mapping_o = {
    "Sandy silt": "ML", "Silty sand": "SM", "Silty clay": "CL", "Clayey silt": "ML",
    "Clayey sand": "SC", "Peat": "PT", "Sandy clay": "CL", "Silty gravel": "GM",
    "Gravelly clay": "CL", "Clayey gravel": "GC"
}
uscs_mapping={k.lower():v for k,v in uscs_mapping_o.items()}

other_categories = {
    "Asphalt / concrete", "Topsoil / vegetation", "Fill", "Debris",
    "Sedimentary bedrock", "Undifferentiated rock", "Cobbles / boulders",
    "Plutonic bedrock", "Volcanic ash", "Volcanic bedrock", "Metamorphic bedrock"
}
other_categories={k.lower() for k in other_categories}

tbd_categories = {
    "silt": ["ML", "OL", "MH", "OH"],
    "clay": ["CL", "OL", "CH", "OH"],
    "sand": ["SW", "SP", "SM", "SC"],
    "gravel": ["GW", "GP", "GM", "GC"]
}
tbd_categories={k.lower():v for k,v in tbd_categories.items()}

dict_uscsRules_keyword = {
    "GW": {"ukeywords": ["well graded gravel"], 
           "keywords": ["gravel sand mixture", "sand gravel cobble mixture", "little fine", "no fine"], 
           "group": "gravel"},
    "GP": {"ukeywords": ["poorly graded gravel"], 
           "keywords": ["gravel sand mixture", "sand gravel cobble mixture", "little fine", "no fine"], 
           "group": "gravel"},
    "GM": {"ukeywords": ["silty gravel", "gravel sand silt mixture"], 
           "keywords": ["with fine"], 
           "group": "gravel"},
    "GC": {"ukeywords": ["clayed gravel", "gravel sand clay mixture"], 
           "keywords": ["with fine"], 
           "group": "gravel"},
    "SW": {"ukeywords": ["well graded sand"], 
           "keywords": ["gravelly sand", "little fine", "no fine"], 
           "group": "sand"},
    "SP": {"ukeywords": ["poorly graded sand"], 
           "keywords": ["gravelly sand", "little fine", "no fine"], 
           "group": "sand"},
    "SM": {"ukeywords": ["silty sand", "sand silt mixture"], 
           "keywords": ["with fine"], 
           "group": "sand"},
    "SC": {"ukeywords": ["clayed sand", "sand clay mixture"], 
           "keywords": ["with fine"], 
           "group": "sand"},
    "ML": {"ukeywords": ["very fine sand", "rock flour", "silty fine sand", "clayey fine sand", "clayey silt", "slight plasticity"], 
           "keywords": ["inorganic silt"], 
           "group": "silt"},
    "CL": {"ukeywords": ["low to medium plasticity", "gravelly clay", "sandy clay", "silty clay", "lean clay"], 
           "keywords": ["inorganic clay"], 
           "group": "clay"},
    "OL": {"ukeywords": ["organic silty clay", "low plasticity"], 
           "keywords": ["organic silt", "organic silt", "organic clay"], 
           "group": "organic silt"},
    "MH": {"ukeywords": ["micaceous fine", "diatomaceous fine", "sandy soil", "silty soil", "elastic silt"], 
           "keywords": ["inorganic silt"], 
           "group": "silt"},
    "CH": {"ukeywords": ["high plasticity", "fat clay"], 
           "keywords": ["inorganic clay"], 
           "group": "clay"},
    "OH": {"ukeywords": ["organic clay", "medium to high plasticity"], 
           "keywords": ["organic silt", "organic silt", "organic clay"], 
           "group": "organic silt"},
    "PT": {"ukeywords": ["peat", "highly organic soils"], 
           "keywords": ["highly organic"], 
           "group": "pt"}
}

dictlith_other = {
    "Fill": "Fill",
    "Asphalt / concrete": "Asphalt or concrete",
    "Topsoil / vegetation": "Topsoil or vegetation",
    "Sedimentary bedrock": "Bedrock",
    "Volcanic bedrock": "Bedrock",
    "Debris": "Fill",
    "Cobbles / boulders": "GP",
    "Undifferentiated rock": "Bedrock",
    "Volcanic ash": "Volcanic ash",
    "Plutonic bedrock": "Bedrock",
    "Metamorphic bedrock": "Bedrock"
}

# mapping func
nltk.download("punkt")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
nlp = spacy.load("en_core_web_md")

def lemmatize_plurals_only(text):
    words = word_tokenize(text)
    lemmatized_words = [lemmatizer.lemmatize(word, pos='n') for word in words]
    return " ".join(lemmatized_words)

def match_comprehensive(description, lithology, standards, tbd_standards, other_standards, map_standards):
    description = description.lower()
    description = lemmatize_plurals_only(description)
    lithology = lithology.lower()
    if lithology in map_standards.keys():
        return map_standards[lithology]
    elif lithology in other_standards:
        return "other"
    elif lithology in tbd_standards.keys():
        uscs_backups=tbd_standards[lithology]
        uscs_backups_re=[]
        for u in uscs_backups:
            for word in standards[u]["ukeywords"]:
                if word in description:
                    return u
            for word in standards[u]["keywords"]:
                if word in description:
                    uscs_backups_re.append(u)
        if uscs_backups_re==[]: uscs_backups_re=uscs_backups
        uscs_scores={u:0 for u in uscs_backups_re}
        for u in uscs_backups_re:
            std_full_list=standards[u]["ukeywords"] + standards[u]["keywords"]
            stf_full='; '.join(std_full_list)
            stf_full=stf_full.lower()
            stf_full_nlp=nlp(stf_full)
            description_nlp=nlp(description)
            uscs_scores[u]=stf_full_nlp.similarity(description_nlp)
        return max(uscs_scores, key=uscs_scores.get)
    else:
        return "incorrect"

def match_map(row):
    return match_comprehensive(row["Description"], row["Lithology"], dict_uscsRules_keyword, tbd_categories, other_categories, uscs_mapping)

# apply & cleanup
f2['USCSre_desc']=f2.apply(match_map, axis=1)
f2['USCSre_desc']=f2['Lithology'].map(dictlith_other).fillna(f2['USCSre_desc'])

f2=f2[f2['USCSre_desc'] != 'incorrect']
f2=f2[['Borehole ID', 'Sub Borehole Layer', 'Top Depth', 'Bottom Depth', 'USCSre_desc']]
f2.columns=['Borehole ID', 'Sub Borehole Layer', 'Top Depth', 'Bottom Depth', 'USCS']
f2.to_csv(path_export, index=False)