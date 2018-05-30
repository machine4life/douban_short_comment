# coding=utf-8
import sys

import gensim
import jieba

reload(sys)
sys.setdefaultencoding("utf-8")

comments = jieba.cut("自己知道在哪里")

model = gensim.models.Word2Vec.load("data/word2vec_gensim")

for comment in comments:
    print model.wv[str(comment)]
