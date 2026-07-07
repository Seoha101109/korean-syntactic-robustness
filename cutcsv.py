import pandas as pd
import re

input = r"C:\Users\family\Desktop\설곽\연구\데이터셋\batch 2\batch\batch_work.csv"
temp = r"C:\Users\family\Desktop\설곽\연구\데이터셋\batch 2\batch\batch_temp.csv"
output = r"C:\Users\family\Desktop\설곽\연구\데이터셋\batch 2\batch\batch_outcome2.csv"

n = 551
#마지막 인덱스+1을 n으로

with open(input, 'r', encoding='utf-8') as f_in, open(temp, 'w', encoding='utf-8', newline='') as f_out:
    for i, line in enumerate(f_in):
        if i == 0:
                f_out.write(line)
                continue
        if i<=n:
            parts = line.strip().split(',')
        
            row_start = parts[:3]
            row_end = parts[-2:]
            
            middle = ",".join(parts[3:-2])
            
            middle = middle.replace('"', "'").replace('“', "'").replace('”', "'")
            middle = middle.strip("'")
            
            safe_sentence = f'"{middle}"'
            

            new_line = ",".join(row_start + [safe_sentence] + row_end) + "\n"
            f_out.write(new_line)

df = pd.read_csv(temp, nrows=n)
df = df.dropna()

df.to_csv(output, index=False, encoding='utf-8-sig')
