import pandas as pd
import json

path1 = r"C:\Users\family\Desktop\SSHS\연구\데이터셋\NIKL_DP_CSV\NIKL_DP_CSV_구문분석 말뭉치\NXDP1902103231_1.csv"
path2 = r"C:\Users\family\Desktop\SSHS\연구\데이터셋\NIKL_DP_CSV\NIKL_DP_CSV_구문분석 말뭉치\NXDP1902103231_2.csv"
path3 = r"C:\Users\family\Desktop\SSHS\연구\데이터셋\NIKL_DP_CSV\NIKL_DP_CSV_구문분석 말뭉치\NXDP1902103231_3.csv"

data1 = pd.read_csv(path1)
data2 = pd.read_csv(path2)
data3 = pd.read_csv(path3)

df_combined = pd.concat([data1,data2,data3], ignore_index=True)

df_unique = df_combined.drop_duplicates(subset=['sentence'], keep='first')

num = 293

sample1 = df_unique.sample(n=num)
sample2 = df_unique.sample(n=num)

savepath = r"C:\Users\family\Desktop\SSHS\연구\데이터셋\controlg.jsonl"

with open(savepath,'w',encoding='utf-8') as f:
    for i in range(num):
        data_pair = {
            'composite_sentence': sample1.iloc[i]['sentence'],
            'separate_sentence': sample2.iloc[i]['sentence']
        }
        
        f.write(json.dumps(data_pair, ensure_ascii=False) + '\n')