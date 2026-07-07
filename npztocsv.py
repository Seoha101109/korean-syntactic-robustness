import numpy as np
import pandas as pd

datatp = ["control","original","random"]
model = ["google-bert_bert-base-multilingual-cased",
         "klue_bert-base",
         "klue_roberta-base",
         "monologg_kobert",
         "snunlp_KR-BERT-char16424"]

#google-bert_bert-base-multilingual-cased
#size linenumber = 293, composite maxtoken = 161, separate maxtoken = 185, hidden dimension = 768

#klue_bert-base
#size linenumber = 293, composite maxtoken = 137, separate maxtoken = 155, hidden dimension = 768

#klue_roberta-base
#size linenumber = 293, composite maxtoken = 137, separate maxtoken = 155, hidden dimension = 768

#monologg_kobert
#size linenumber = 293, composite maxtoken = 52, separate maxtoken = 57, hidden dimension = 768

#snunlp_KR-BERT-char16424
#size linenumber = 293, composite maxtoken = 92, separate maxtoken = 98, hidden dimension = 768

for j in range(len(datatp)):
    ty = datatp[j]
    for i in range(len(model)):
        model_name = model[i]
        file = fr"C:\Users\family\Desktop\SSHS\연구\layer_analysis_{ty}\layer_analysis_{ty}\{model_name}\{model_name}_debiased_cka_values"

        data = np.load(file+".npz")

        df = pd.DataFrame({key: data[key] for key in data.keys()})
        df.to_csv(file+".csv", index=False, encoding='utf-8-sig')