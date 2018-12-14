import os
import json
import pickle

from django.http import HttpResponse
from django.shortcuts import render

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, 'static')
TOP_N = 8
DAT_CACHE = 'keywords_trie.pickle'

#现在把词库初始化放在这里为了方便
from .before_runserver import main
main()
keyword_dat = pickle.load(open(os.path.join(STATIC_DIR, DAT_CACHE), 'rb'))


def naive(request):
    userdic = ['ActionScript','AppleScript','Asp','BASIC','C','C++','Clojure','COBOL','ColdFusion','Erlang','Fortran','Groovy','Haskell','Java','JavaScript','Lisp','Perl','PHP','Python','Ruby','Scala','Scheme']
    return render(request, 'hr_search_engine/search.html', {'availableTags': json.dumps(userdic)})


def categories(request):
    return render(request, 'hr_search_engine/categories.html')


def custom(request):
    return render(request, 'hr_search_engine/ajax_search.html')


def query_recommend(request):
    if 'term' in request.GET:
        q_str = request.GET['term']
        if isinstance(q_str, str):
            # 这里是查询并返回联想词的逻辑
            q = q_str.split(' ')[-1]
            _q = ' '.join(q_str.split(' ')[:-1])
            candidates = auto_complete(q)
            print(candidates)
            output = []
            keyword_set = []
            for can in candidates:
                if can['v'] in keyword_set:
                    continue
                else:
                    keyword_set.append(can['v'])
            for kw in keyword_set:
                output.append(_q + ' ' + kw)
            return HttpResponse(json.dumps(output), 'application/json')

    return HttpResponse()


def auto_complete(word):
    candidates = list()
    for candidate in keyword_dat.items(word):
        for word in candidate[1]:
            candidates.append(word)
    rs = sorted(candidates, key=lambda x: x['w'], reverse=True)[:TOP_N]
    return rs


def esquery(request):
    if 'query' in request.GET:
        q_str = request.GET['query']
        return HttpResponse(json.dumps(q_str), 'application/json')
    return HttpResponse()


if __name__ == '__main__':
    print(auto_complete('小'))
