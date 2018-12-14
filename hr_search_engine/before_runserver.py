# -*- coding:utf-8 -*-
"""
@author:TANYIPENG631
@file: before_runserver.py
@time: 2018/12/11  18:16
"""
import os
import pickle

from pypinyin import lazy_pinyin, STYLE_INITIALS, STYLE_FINALS
import datrie

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, 'static')

PINYIN_CONFUSION_LIST = [('c', 'ch'), ('z', 'zh'), ('s', 'sh'), ('in', 'ing'), ('en', 'eng')]
PINYIN_CONFUSION_MAP = {}
for tu in PINYIN_CONFUSION_LIST:
    PINYIN_CONFUSION_MAP[tu[0]] = tu[1]
    PINYIN_CONFUSION_MAP[tu[1]] = tu[0]
DEFAULT_CATEGORY = 'all'
DEFAULT_WEIGHT = 10

KEYWORDS_PREPARED_FILE = 'keywords_prepared.txt'
DAT_CACHE = 'keywords_trie.pickle'


def prepare_keywords(keywords_conf_file, keywords_prepared_file):
    keyword_dict = dict()
    with open(keywords_conf_file, 'r', encoding='utf8') as kw_input:
        for line in kw_input:
            if len(line.split('\t')) == 1:
                key = line.strip().split('\t')[0]
                keyword_dict[key] = {'c': DEFAULT_CATEGORY, 'w': DEFAULT_WEIGHT}
            elif len(line.split('\t')) == 3:
                key, weight_str, category = line.strip().split('\t')
                try:
                    weight = int(weight_str)
                except:
                    continue
                keyword_dict[key] = {'c': category, 'w': weight}
            elif len(line.split('\t')) == 2:
                key, weight_str = line.strip().split('\t')
                try:
                    weight = int(weight_str)
                except:
                    continue
                keyword_dict[key] = {'c': DEFAULT_CATEGORY, 'w': weight}
            elif len(line.split('\t')) == 4:
                key, weight_str, category, kws_str = line.strip().split('\t')
                try:
                    weight = int(weight_str)
                    kws = [item.sctrip() for item in kws_str.strip().split(',')]
                except:
                    continue
                keyword_dict[key] = {'c': category, 'w': weight, 'k': kws}

    with open(keywords_prepared_file, 'w', encoding='utf8') as kw_ouput:
        for keyword, info in keyword_dict.items():
            initial = lazy_pinyin(keyword, errors='ignore', style=STYLE_INITIALS)
            full = lazy_pinyin(keyword, errors='ignore')
            for (i, ii) in enumerate(initial):
                if not ii:
                    initial[i] = full[i][0]
            finals = lazy_pinyin(keyword, errors='ignore', style=STYLE_FINALS)
            splited = list(zip(initial, finals))
            kw_ouput.write('{}\t{}\t{}\t{}\n'.format(keyword, keyword, info['w'], info['c']))
            if 'k' in info:
                for term in info['k']:
                    kw_ouput.write('{}\t{}\t{}\t{}\n'.format(term, keyword, info['w'], info['c']))
            if full and splited and len(full) == len(splited):
                ids = list()
                initials = ['']
                variants = ['']
                ids.append(''.join(full))  # full pinyin
                for char in splited:
                    if char[0] in PINYIN_CONFUSION_MAP:
                        ii = [char[0], PINYIN_CONFUSION_MAP[char[0]]]
                    else:
                        ii = [char[0]]
                    _initials = []
                    for ini in initials:
                        for i in ii:
                            _initials.append(ini + i)
                    initials = _initials
                    if char[1] in PINYIN_CONFUSION_MAP:
                        ff = [char[1], PINYIN_CONFUSION_MAP[char[1]]]
                    else:
                        ff = [char[1]]
                    char_variant = []
                    for i in ii:
                        for f in ff:
                            char_variant.append(''.join((i, f)))  # confused variants
                    _variants = []
                    for variant in variants:
                        for v in char_variant:
                            _variants.append(variant + v)
                    variants = _variants
                ids.extend(variants)
                ids.extend(initials)
                ids = set(ids)
                for id in ids:
                    kw_ouput.write('{}\t{}\t{}\t{}\n'.format(id, keyword, info['w'], info['c']))
                    # TODO: 还没有实现拼音对别名的联想


def prepare_keyword_trie(keyword_file):
    keyword_list = []
    keys = ''
    with open(keyword_file, 'r', encoding='utf8') as kw_file:
        for line in kw_file:
            if len(line.split('\t')) == 4:
                key, value, weight_str, category = line.strip().split('\t')
                try:
                    weight = int(weight_str)
                except:
                    continue
                keyword_list.append({'k': key, 'v': value, 'w': weight, 'c': category})
                keys += key
    chars = set(keys)
    kw_trie = datrie.Trie(''.join(chars))
    for keyword in keyword_list:
        if keyword['k'] in kw_trie:
            value = kw_trie[keyword['k']]
            value.append(keyword)
            kw_trie[keyword['k']] = value
        else:
            kw_trie[keyword['k']] = [keyword]
    return kw_trie


def main():
    keyword_conf_file = os.path.join(STATIC_DIR, 'keywords_raw.txt')
    keyword_prepared_file = os.path.join(STATIC_DIR, KEYWORDS_PREPARED_FILE)
    prepare_keywords(keyword_conf_file, keyword_prepared_file)
    keyword_dat = prepare_keyword_trie(os.path.join(STATIC_DIR, KEYWORDS_PREPARED_FILE))
    with open(os.path.join(STATIC_DIR, DAT_CACHE), 'wb') as dat_pickle:
        pickle.dump(keyword_dat, dat_pickle)


if __name__ == '__main__':
    main()




