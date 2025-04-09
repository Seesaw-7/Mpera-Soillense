import pandas as pd
import numpy as np


path_f1='./Data/Data_raw/File_1_with_elevation.csv'
# path_f2re='./Data/Data_result/file_2_reUSCS.csv'
path_f2re='./Data/Data_result/file_2_originalUSCSclean.csv'
# path_export='./Data/Data_result/file_2_reUSCS_sampling_withelevation.csv'
path_export='./Data/Data_result/file_2_originalUSCSclean_sampling_withelevation.csv'

f1=pd.read_csv(path_f1)
f2_o=pd.read_csv(path_f2re)

# preprocess
f1.sort_values(by=['Elevation'], inplace=True)
f2=f2_o[f2_o['USCS']!='incorrect']
f2.dropna(subset=['Top Depth', 'Bottom Depth'], inplace=True)
f2['Total Depth'] = f2['Bottom Depth'] - f2['Top Depth']
f2['Total Depth'] = f2['Total Depth'].abs()
f2.drop(columns=['Sub Borehole Layer', 'Description', 'Lithology'], inplace=True, axis=1)

# sampling
def generate_sampling_depths(top, bottom, total, grid=4):
    top=min(top, bottom)
    bottom=max(top, bottom)
    if total<=2*grid:
        return [(top+bottom)/2]
    elif total <= 4*grid:
        return [(2*top+bottom)/3, (top+2*bottom)/3]
    else:
        return [top+grid, (top+bottom)/2, bottom-grid]

expanded_data = []

for _, row in f2.iterrows():
    borehole_id = row['Borehole ID']
    top_depth = row['Top Depth']
    bottom_depth = row['Bottom Depth']
    uscs = row['USCS']
    total_depth = row['Total Depth']
    
    sampling_depths = generate_sampling_depths(top_depth, bottom_depth, total_depth)
    
    for depth in sampling_depths:
        expanded_data.append({'Borehole ID': borehole_id, 'Sampling Depth': depth, 'USCS': uscs})

df_expanded = pd.DataFrame(expanded_data)

df_expanded = df_expanded.merge(f1, on='Borehole ID', how='left')
df_expanded['Sampling Elevation'] = df_expanded['Elevation'] - df_expanded['Sampling Depth']
df_sampling=df_expanded[['Borehole ID', 'Document ID', 'Latitude', 'Longitude', 'Elevation', 'Sampling Depth', 'Sampling Elevation', 'USCS']]
df_sampling.dropna()

df_sampling.to_csv(path_export, index=False)