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
    
    ####################################

    #DELETE APP DATABASE
    #APP NUMBER
    app = 17

    ####################################

    if app == 17:
        URL2 = ''
        API_TOKEN2 = ""
    if app == 16:
        URL2 = ''
        API_TOKEN1 = ""

    URL = ''
    
    API_TOKEN = ""
    RESP = get_kintone(URL2, API_TOKEN2)
    # print(RESP.text)
    with open('osusume_kiji.json', mode='wt', encoding='utf-8') as file:
        file.write(RESP.text)

    a = open("osusume_kiji.json","r") #ここが(1)
    a = json.load(a) #ここが(2)
    code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')
    id_list = []#削除用
    user={}
    not_unique = ["更新者", "ユーザー選択","作成者","日時","作成日時","$id","更新日時","文字列__1行__8","$revision","文字列__1行__10","添付ファイル","星座"]
    for i in a["records"]:
        l=[]
        for k, v in i.items():
            
            if k == "レコード番号":#レコード番号は別に保存
                id = int(v["value"])
                id_list.append(id)
            
            if k == "文字列__1行__14":#レコード番号は別に保存
                id = str(v["value"])
                # id_list.append(id)
            elif k not in not_unique:
                # l = l + str(v["value"]).replace("\n", " ")+" "
                p = str(v["value"]).replace("\n", " ")
                p = code_regex.sub('', p)
                p = re.sub("[a-zA-Z]","",p)
                l.append(p)
       
        user[id]=l

    print(id_list)
    
    PARAMS_del = {}
    if app == 16:
        PARAMS_del["app"] = 16
    elif app == 17:
        PARAMS_del["app"] = 17
    PARAMS_del["ids"] = id_list
    
    RESP = delete_kintone(URL1, API_TOKEN2, PARAMS_del)
    print(RESP.text)
    
    