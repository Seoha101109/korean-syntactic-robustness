import pandas as pd
import json
import re

input_file = r"C:\Users\family\Desktop\설곽\연구\데이터셋\batch 2\batch\batch_outcome2.csv"
output_file = r"C:\Users\family\Desktop\설곽\연구\데이터셋\batch 2\batch\batch_processed2.jsonl"

df = pd.read_csv(input_file)

df = df[df['status'] != 'x']

pars = ['(', ')', '[', ']']
pars_open = ['(', '[']
pars_close = [')', ']']

def skeleton_sentence(sentence, status):
    s = sentence
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'\([^)]*\)', '', s)
    i = 0
    while "[" in s:
        if any(status[i] == p for p in "mn"):
            s = re.sub(r'^([^\[]*)\[','그러한 ',s)
        else:
            s = re.sub(r'^([^\[]*)\[','그 ',s)
        i += 1
    s = s.replace("]","").replace("/","")
    s = " ".join(s.split()).strip()

    if not s.endswith('.'):
        s += '.'

    skeleton_obj = {
        "conj": "ROOT",
        "target_text": "NONE",
        "sentence": s,
        "status": "main",
        "tense": "main"
    }
    
    return skeleton_obj

    
def par_in(word):
    if any(p in word for p in pars):
        return True
    return False

def par_size(letter):
    if letter in '()':
        return 'S'
    if letter in '[]':
        return 'B'

def get_nested(l, attr):
    # print('ㅗ', l, attr)
    if len(attr) ==0:
        return l

    first = attr[0]
    return get_nested(l[first], attr[1:])

def add_conj(l, word):
    if len(word) >= 2 and word[0] == word[-1] == '/':
        l.append(word)

def strip1(sentence):
    result = []
    cur_list = result
    list_attr = {}
    cur_attr = [-1]
    conj = []
    stripped_sent = sentence.strip().split()
    for word in stripped_sent:
        if not par_in(word):
            cur_list.append(word)
            add_conj(conj, word)
            cur_attr[-1] += 1 # 이 시점의 cur_attr 과 result 가 대응
            # print(cur_attr, result)
        else:
            word_cut = ''
            for letter in word:

                if not letter in pars:
                    word_cut += letter
                else:
                    if not word_cut == '':
                        cur_list.append(word_cut)
                        add_conj(conj, word_cut)
                        cur_attr[-1] += 1
                        word_cut = ''
                        # print(cur_attr, result)
                    if letter in pars_open:
                        cur_list.append([])
                        cur_attr[-1] += 1
                        list_attr[tuple(cur_attr)] = par_size(letter)
                        cur_attr.append(-1)
                        cur_list = cur_list[-1]
                        # print(cur_attr, result)
                    if letter in pars_close:
                        cur_attr.pop()
                        cur_list = get_nested(result, cur_attr[:-1]) #cur_attr 에 해당하는 번지를 cur_list 로 설정하기
                        # cur_attr[-1] += 1
                        # print(cur_attr, result)
            if not word_cut == '':
                cur_list.append(word_cut)
                add_conj(conj, word_cut)
                cur_attr[-1] += 1
                # print(cur_attr, result)
                word_cut = '' 
    return result, list_attr, conj

# print(strip1('오 시장은 ((/""지난/) [5개월]간 /겪어본/) [시의회]는 무상급식을 앞세워 (이와 /비슷한/) (/무분별한/) [[퍼주기 정책]]을 계속 내놓을 것으로 생각된다""며 ""이번에 확실하게 쐐기를 박아야 한다고 판단했다""고 말했다.'))


# print(df.head())


def is_conj_word(x):
    return isinstance(x, str) and len(x) >= 2 and x[0] == x[-1] == '/'

def clean_conj(word):
    return word.strip('/').replace('""', '')

def flatten_words(x):
    if isinstance(x, str):
        return [x]

    result = []
    for item in x:
        result.extend(flatten_words(item))
    return result

def phrase(x):
    return ' '.join(flatten_words(x))

def find_conj_paths(l, path=()):
    paths = []

    for i, item in enumerate(l):
        cur_path = path + (i,)

        if isinstance(item, list):
            paths.extend(find_conj_paths(item, cur_path))
        elif is_conj_word(item):
            paths.append(cur_path)

    return paths

def only_conj_phrase(x):
    words = flatten_words(x)
    return len(words) > 0 and all(is_conj_word(w) for w in words)

def find_target_path(result, conj_path):
    """
    conj_path를 기준으로 피수식어 path 찾기.
    예:
    /지난/ -> [5개월]
    /겪어본/ -> [시의회]
    /비슷한/, /무분별한/ -> [[퍼주기 정책]]
    """

    # 1. /지난/ 처럼 괄호 안에 관형사 하나만 있는 경우
    parent_path = conj_path[:-1]
    parent = get_nested(result, parent_path)

    if isinstance(parent, list) and len(parent) == 1:
        grand_path = conj_path[:-2]
        parent_idx = conj_path[-2]

        return grand_path + (parent_idx + 1,)

    # 2. 일반 관형사구: 현재 괄호 리스트의 다음 형제 탐색
    clause_path = conj_path[:-1]
    outer_path = clause_path[:-1]
    clause_idx = clause_path[-1]

    outer = get_nested(result, outer_path)

    i = clause_idx + 1
    while i < len(outer):
        candidate_path = outer_path + (i,)
        candidate = get_nested(result, candidate_path)

        # (/무분별한/) 같은 관형사구만 있는 건 건너뜀
        if only_conj_phrase(candidate):
            i += 1
            continue

        # 야당의, 정부의, 그의 같은 소유/관형 modifier는 건너뜀
        if is_possessive_modifier(candidate):
            i += 1
            continue

        return candidate_path

    return None

def is_possessive_modifier(x):
    return isinstance(x, str) and x.endswith('의')

def status_to_josa(status):
    status = status.upper()

    if status == 'A':
        return '이/가'
    if status == 'B':
        return '은/는'
    if status == 'C':
        return '을/를'
    if status in ['E', 'G', 'K']:
        return '에'
    if status == 'F':
        return '에서'
    if status == 'H':
        return '로/으로'
    if status in ['M', 'N', 'O', 'P']:
        return '='
    if status == 'Q':
        return '이/가'
    if status == 'R':
        return '라는'

    return '?'

def make_appositive_sentence(context, conj_text, tense):
    pred = conj_to_final(conj_text, tense)

    if context:
        return f'{context} {pred}.'

    return f'{pred}.'

def split_tense(tense):
    return [tense[i:i+2] for i in range(0, len(tense), 2)]


# sentence = '오 시장은 ((/""지난/) [5개월]간 /겪어본/) [시의회]는 무상급식을 앞세워 (이와 /비슷한/) (/무분별한/) [[퍼주기 정책]]을 계속 내놓을 것으로 생각된다""며 ""이번에 확실하게 쐐기를 박아야 한다고 판단했다""고 말했다.'

# print(strip2(sentence, 'acaa', 'ptptpsps'))

def has_jongseong(word):
    if not word:
        return False

    last = word[-1]
    code = ord(last)

    if not (0xAC00 <= code <= 0xD7A3):
        return False

    return (code - 0xAC00) % 28 != 0


def choose_josa(word, pair):
    a, b = pair.split('/')

    if has_jongseong(word):
        return a
    return b


def final_josa(target_text, status):
    status = status.upper()

    if status == 'A':
        return choose_josa(target_text, '이/가')

    if status == 'B':
        return choose_josa(target_text, '은/는')

    if status == 'C':
        return choose_josa(target_text, '을/를')

    if status in ['E', 'G', 'K']:
        return '에'

    if status == 'F':
        return '에서'

    if status == 'H':
        return choose_josa(target_text, '으로/로')

    if status in ['M', 'N', 'O', 'P']:
        return '는'

    if status == 'Q':
        return choose_josa(target_text, '이/가')

    if status == 'R':
        return '라는'

    return ''


ENDING_DICT = {
    '지난': '지났다',
    '겪어본': '겪어봤다',
    '비슷한': '비슷하다',
    '무분별한': '무분별하다',
    '이용하려는': '이용하려다',
}


def conj_to_final(conj_text, tense):
    if conj_text in ENDING_DICT:
        return ENDING_DICT[conj_text]

    # 가장 단순한 fallback
    if conj_text.endswith('한'):
        return conj_text[:-1] + '하다'

    if conj_text.endswith('한'):
        return conj_text[:-1] + '했다'

    if conj_text.endswith('던'):
        return conj_text[:-1] + '았다'

    if conj_text.endswith('은'):
        return conj_text[:-1] + '었다'

    if conj_text.endswith('는'):
        return conj_text[:-1] + '다'

    if conj_text.endswith('ㄹ') or conj_text.endswith('을'):
        return conj_text + ' 것이다'

    return conj_text + '다'

def make_final_sentence(target_text, conj_text, status, tense):
    josa = final_josa(target_text, status)
    pred = conj_to_final(conj_text, tense)

    if josa == '=':
        return f'{target_text}은 {pred}.'

    if josa:
        return f'{target_text}{josa} {pred}.'

    return f'{target_text} {pred}.'

def remove_conj_words(x):
    if isinstance(x, str):
        if is_conj_word(x):
            return []
        return [x]

    result = []
    for item in x:
        result.extend(remove_conj_words(item))
    return result

def get_context_words_for_conj(result, conj_path, target_path):
    clause_path = conj_path[:-1]
    clause = get_nested(result, clause_path)

    context = []

    for i, item in enumerate(clause):
        item_path = clause_path + (i,)

        if item_path == conj_path:
            continue

        # 피수식어 자체는 context에서 제외
        if target_path is not None and item_path == target_path:
            continue

        # 관형사는 제거하되, 그 안의 일반 단어는 살림
        context.extend(remove_conj_words(item))

    return ' '.join(context)

def make_final_sentence(target_text, conj_text, status, tense, context=''):
    josa = final_josa(target_text, status)
    pred = conj_to_final(conj_text, tense)

    mid = ''
    if context:
        mid = ' ' + context

    if josa:
        return f'{target_text}{josa}{mid} {pred}.'

    return f'{target_text}{mid} {pred}.'

def strip2(sentence, status, tense):
    result, list_attr, conj = strip1(sentence)

    conj_paths = find_conj_paths(result)
    tense_list = split_tense(tense)

    if len(conj) != len(status):
        raise ValueError(f'관형사 수({len(conj)})와 status 수({len(status)})가 다름')

    if len(conj) != len(tense_list):
        raise ValueError(f'관형사 수({len(conj)})와 tense 수({len(tense_list)})가 다름')

    output = []

    for conj_word, conj_path, st, te in zip(conj, conj_paths, status, tense_list):
        conj_text = clean_conj(conj_word)

        if st.upper() == 'X' or te.upper() == 'XX':
            continue

        # 동격 관형절
        if st.upper() in ['M', 'N', 'O', 'P']:
            context = get_context_words_for_conj(result, conj_path, None)

            final_sentence = make_appositive_sentence(
                context,
                conj_text,
                te
            )

            output.append({
                'conj': conj_word,
                'conj_clean': conj_text,
                'conj_path': conj_path,
                'target_path': None,
                'target': None,
                'target_text': None,
                'status': st,
                'tense': te,
                'context': context,
                'sentence': final_sentence
            })

            continue

        target_path = find_target_path(result, conj_path)

        if target_path is None:
            target = None
            target_text = None
            context = ''
            final_sentence = None
        else:
            target = get_nested(result, target_path)
            target_text = phrase(target)

            conj_text = clean_conj(conj_word)

            context = get_context_words_for_conj(result, conj_path, target_path)

            final_sentence = make_final_sentence(
                target_text,
                conj_text,
                st,
                te,
                context
            )

        output.append({
            'conj': conj_word,
            'conj_clean': clean_conj(conj_word),
            'conj_path': conj_path,
            'target_path': target_path,
            'target': target,
            'target_text': target_text,
            'status': st,
            'tense': te,
            'context': context,
            'sentence': final_sentence
        })

    output.append(skeleton_sentence(sentence, status))
    return output


with open(output_file, 'w', encoding='utf-8') as f:
    for _, row in df.iterrows():
        outputs = strip2(str(row['sentence']), str(row['status']), str(row['tense']))
        sentences = [row['sentence'] for row in outputs]
        orgin = str(row['sentence'])
        orgin = orgin.replace("(","").replace(")","").replace("[","").replace("]","").replace("/","")

        data_pair = {
            'composite_sentence': orgin,
            'separate_sentence': " ".join(sentences)
        }
        
        f.write(json.dumps(data_pair, ensure_ascii=False) + '\n')
