
import numpy as np
import glob
import os

datatp = ["shuffled","original","random"]
model = ["google-bert_bert-base-multilingual-cased",
         "klue_bert-base",
         "klue_roberta-base",
         "monologg_kobert",
         "snunlp_KR-BERT-char16424"]

def trapz_area(y):
    y = np.asarray(y, dtype=float)
    return float(np.sum((y[:-1] + y[1:]) / 2.0))


def load_layerwise_means(filepath):
    data = np.load(filepath)
    if 'means' not in data:
        raise KeyError(f"{filepath}에 'means' 키가 없습니다. 실제 키: {list(data.keys())}")
    return data['means']


def compute_all(folder='.'):
    models = ["google-bert_bert-base-multilingual-cased",
         "klue_bert-base",
         "klue_roberta-base",
         "monologg_kobert",
         "snunlp_KR-BERT-char16424"]

    results = []
    for model in models:
        paths = {
            'original': fr"C:\Users\family\Desktop\SSHS\연구\layer_analysis_original\{model}\{model}_debiased_cka_values.npz",
            'shuffle':  fr"C:\Users\family\Desktop\SSHS\연구\layer_analysis_shuffled\{model}\{model}_debiased_cka_values.npz",
            'random':   fr"C:\Users\family\Desktop\SSHS\연구\layer_analysis_random\{model}\{model}_debiased_cka_values.npz",
        }

        means = {k: load_layerwise_means(p) for k, p in paths.items()}

        for k, arr in means.items():
            if len(arr) != 13:
                print(f"[경고] {model}-{k}: 레이어 수가 13이 아닙니다 (실제 {len(arr)}개)")

        auc_original = trapz_area(means['original'])
        auc_shuffle = trapz_area(means['shuffle'])
        auc_random = trapz_area(means['random'])

        denominator = auc_original - auc_random
        if abs(denominator) < 1e-9:
            robustness = float('nan')
            print(f"[경고] {model}: 분모(AUC_original - AUC_random)가 0에 가까워 계산 불가")
        else:
            robustness = (auc_original - auc_shuffle) / denominator

        results.append({
            'model': model,
            'AUC_original': auc_original,
            'AUC_shuffle': auc_shuffle,
            'AUC_random': auc_random,
            'Robustness': robustness,
        })

    if not results:
        return

    results.sort(key=lambda r: -r['Robustness'])

    print(f"\n{'모델':<40}{'AUC(Original)':>15}{'AUC(Shuffle)':>15}{'AUC(Random)':>13}{'Robustness':>13}")
    print("-" * 96)
    for r in results:
        print(f"{r['model']:<40}{r['AUC_original']:>15.4f}{r['AUC_shuffle']:>15.4f}"
              f"{r['AUC_random']:>13.4f}{r['Robustness']:>13.4f}")

    print(f"\n순위: {' > '.join(r['model'] for r in results)}")


if __name__ == '__main__':
    compute_all(folder='.')