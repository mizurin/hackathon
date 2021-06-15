from os import supports_bytes_environ
import requests
import json
import ast
import gensim
import pprint
from scipy import spatial
import itertools
import numpy as np
import MeCab
import re
import traceback
from collections import defaultdict

mecab = MeCab.Tagger("-Owakati")


URL1 = ""

def get_kintone(url, api_token):
    """kintoneのレコードを1件取得する関数"""
    headers = {"X-Cybozu-API-Token": api_token}
    resp = requests.get(url, headers=headers)

    return resp

def post_kintone(url, api_token, params):
    """kintoneにレコードを1件登録する関数"""
    headers = {"X-Cybozu-API-Token": api_token, "Content-Type" : "application/json"}
    resp = requests.post(url, json=params, headers=headers)

    return resp

def delete_kintone(url, api_token, params):
    """kintoneにレコードを1件削除する関数"""
    headers = {"X-Cybozu-API-Token": api_token, "Content-Type" : "application/json"}
    resp = requests.delete(url, json=params, headers=headers)

    return resp

def avg_feature_vector(sentence, model, num_features):
    words = mecab.parse(sentence).replace(' \n', '').split() # mecabの分かち書きでは最後に改行(\n)が出力されてしまうため、除去
    feature_vec = np.zeros((num_features,), dtype="float32") # 特徴ベクトルの入れ物を初期化
    for word in words:
        feature_vec = np.add(feature_vec, model[word])
    if len(words) > 0:
        feature_vec = np.divide(feature_vec, len(words))
    return feature_vec

def sentence_similarity(sentence_1, sentence_2):
    # 今回使うWord2Vecのモデルは300次元の特徴ベクトルで生成されているので、num_featuresも300に指定
    num_features=300
    sentence_1_avg_vector = avg_feature_vector(sentence_1, word2vec_model, num_features)
    sentence_2_avg_vector = avg_feature_vector(sentence_2, word2vec_model, num_features)
    # １からベクトル間の距離を引いてあげることで、コサイン類似度を計算
    return 1 - spatial.distance.cosine(sentence_1_avg_vector, sentence_2_avg_vector)

if __name__ == "__main__":
    
    URL = ''
    API_TOKEN = ""
    API_TOKEN1 = ""
    RESP = get_kintone(URL, API_TOKEN)
    # print(RESP.text)
    with open('kintone.json', mode='wt', encoding='utf-8') as file:
        file.write(RESP.text)
    
    # json_str = json.dumps(RESP.text)
    a = open("kintone.json","r") #ここが(1)
    a = json.load(a) #ここが(2)
    code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')
    id_list = []#削除用
    user={}
    not_unique = ["更新者", "ユーザー選択","作成者","日時","作成日時","$id","更新日時","文字列__1行__8","$revision","文字列__1行__10","添付ファイル","星座"]
    for i in a["records"]:
        l=[]
        for k, v in i.items():
            """
            if k == "レコード番号":#レコード番号は別に保存
                id = int(v["value"])
                id_list.append(id)
            """
            if k == "文字列__1行__14":#レコード番号は別に保存
                id = str(v["value"])
                # id_list.append(id)
            elif k not in not_unique:
                # l = l + str(v["value"]).replace("\n", " ")+" "
                p = str(v["value"]).replace("\n", " ")
                p = code_regex.sub('', p)
                p = re.sub("[a-zA-Z]","",p)
                l.append(p)
        # l = code_regex.sub('', l)
        # l = re.sub("[a-zA-Z]","",l)
        # print(l)
        user[id]=l
            # print(i["value"])
    word2vec_model = gensim.models.KeyedVectors.load_word2vec_format('model.vec', binary=False)
    
    sim = {}
    for num in itertools.combinations(user.keys(), 2):
        # print(num)
        print(user[num[0]],user[num[1]])
        tmp_sim=0
        for i, j in zip(user[num[0]],user[num[1]]):
            print(i,j)
            try:
                if np.isnan(sentence_similarity(i,j)):
                    pass
                else:
                    tmp_sim += sentence_similarity(i,j)
                print(tmp_sim)
            except KeyError:
                # t = traceback.format_exc()
                # print(t)
                pass
        sim[num] = tmp_sim
        # print(tmp_sim)
    sort_sim={}
    for k, v in sim.items():
        sort_sim[k[0],k[1]] = v
        sort_sim[k[1],k[0]] = v
        print(k[0],k[1],v)
        print(k[1],k[0],v)
    
    sorted_sim = sorted(sort_sim.items(), key=lambda x: (x[0][0], x[1]), reverse=True)
        
    # for k in sorted_sim:
    #     print(k)
    tmp = -1
    # result = defaultdict(dict)
    cnt=0
    result_list =[]
    for k in sorted_sim:
        if cnt >=5:
            if tmp == k[0][0]:
                continue
            else:
                cnt=0
        
        if cnt == 0:
            result = {}
            result["文字列__1行_"] = {}
            result["文字列__1行_"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行_"]["value"] = k[0][0]
            
            result["文字列__1行__0"] = {}
            result["文字列__1行__0"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行__0"]["value"] = k[0][1]
        if cnt == 1:
            result["文字列__1行__1"] = {}
            result["文字列__1行__1"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行__1"]["value"] = k[0][1]
        if cnt == 2:
            result["文字列__1行__2"] = {}
            result["文字列__1行__2"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行__2"]["value"] = k[0][1]
        if cnt == 3:
            result["文字列__1行__3"] = {}
            result["文字列__1行__3"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行__3"]["value"] = k[0][1]
        if cnt == 4:
            result["文字列__1行__4"] = {}
            result["文字列__1行__4"]["type"] = "SINGLE_LINE_TEXT"
            result["文字列__1行__4"]["value"] = k[0][1]
        
        cnt +=1
        if cnt >=5:
            tmp = k[0][0]
            result_list.append(result)

    # print(result_list)

    result_dic = {}
    result_dic["app"]  = 16
    result_dic["records"] = result_list
    pprint.pprint(result_dic)

        

    PARAMS1 = result_dic
    RESP = post_kintone(URL1, API_TOKEN1, PARAMS1)
    print(RESP.text)
    