import pandas as pd
import numpy as np

path_f2_original='./Data/Data_raw/file_2.csv'
path_export='./Data/Data_result/file_2_originalUSCSclean.csv'

f2=pd.read_csv(path_f2_original)

def clean_linebreaks(s):
    if s==None: return None
    s=str(s)
    s = s.replace('\x08', '')
    s = s.strip('\r\n')
    s = s.replace('\r\n', '-')
    s = s.replace(' ', '')
    return s

f2['USCS_clean']=f2['USCS'].apply(clean_linebreaks)

uscs_format=["GW", "GP", "GM", "GC", "SW", "SP", "SM", "SC", "ML", "CL", "OL", "MH", "CH", "OH", "PT"]
uscs_group_map = {
    "GW": "gravel",
    "GP": "gravel",
    "GM": "gravel",
    "GC": "gravel",
    "SW": "sand",
    "SP": "sand",
    "SM": "sand",
    "SC": "sand",
    "ML": "silt",
    "CL": "clay",
    "OL": "organic silt",
    "MH": "silt",
    "CH": "clay",
    "OH": "organic silt",
    "PT": "pt"
}

def clean_validate(s, l_format=uscs_format, dict_group=uscs_group_map):
    if s==None: return None
    if s.count('-') > 1:
        return None
    if ',' in s:
        return None
    if 'No' in s or 'nan' in s:
        return None
    if '-' in s:
        part1, part2 = s.split('-')
        if part1 not in l_format or part2 not in l_format:
            return None
        if part1==part2: return part1
        if dict_group.get(part1) != dict_group.get(part2):
            return None
    if '-' not in s and s not in l_format:
        return None
    return s

f2['USCS_clean']=f2['USCS_clean'].apply(clean_validate)

def clean_joint(s):
    if s==None: return None
    if '-' not in s:
        return s
    if s == 'SP-SM':
        return s
    return s.split('-')[0]
f2['USCS_clean']=f2['USCS_clean'].apply(clean_joint)

f2.drop(columns=['USCS'], inplace=True, axis=1)
f2=f2.rename(columns={'USCS_clean': 'USCS'})
f2.dropna()
f2.to_csv(path_export, index=False)