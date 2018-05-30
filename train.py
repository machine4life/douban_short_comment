# encoding=utf-8
import sys

import jieba
import word2vec

from spider.database import get_comments

reload(sys)
sys.setdefaultencoding("utf-8")


def clear(words):
    return [word for word in words if word != "" and word != " " and word != "，"]

model = word2vec.load('comment_vec.txt', encoding="utf-8")

comment_rating = get_comments(0, 10)

for item in comment_rating:
    comment = item[0]
    words = clear(jieba.cut(comment, cut_all=False, HMM=False))
    print "，".join(words)
    print item[1]
    for word in words:
        if word in model:
            # print model[word]
            pass
        else:
            print word
