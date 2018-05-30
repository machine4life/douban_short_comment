# encoding=utf-8
import jieba

from spider.database import get_comments
from spider.util import sort_by_value

data = []

all_word = [{}, {}, {}, {}, {}, {}]

for i in range(0, 100):
    print "start get page %d" % i
    data = get_comments(i * 2000, 2000)
    for c in data:
        comment = c[0]
        rating = int(c[1])
        words = jieba.cut(comment, cut_all=False)
        for word in words:
            if word in all_word[rating]:
                all_word[rating][word] += 1
            else:
                all_word[rating][word] = 1

min_word_length = 2
show_count = 20

for i in range(1, 6):
    print "===================="
    print "words in rating %d:" % i
    sorted_data = sort_by_value(all_word[i])
    # show_words = {}
    i = 0
    for item in sorted_data:
        if i >= show_count:
            break

        if len(item[0]) > min_word_length:
            i += 1
            # show_words[item[0]] = item[1]
            print "word : [%s]   count : %d" % item

    print "===================="

