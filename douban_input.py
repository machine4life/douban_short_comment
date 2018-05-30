# coding=utf-8
import gensim
import jieba
import tflearn

from spider.database import get_bad_comments, get_middle_comments, get_good_comments

TRAIN_INDEX = 30
TEST_INDEX = 40
PREDICT_INDEX = 41


def process_data(comments):
    train_x = []
    train_y = []
    model = gensim.models.Word2Vec.load("data/word2vec_gensim")
    comment_size = len(comments)
    for i in range(0, len(comments)):
        comment = comments[i]
        words = jieba.cut(comment[0])
        wordvec = []
        for word in words:
            if not word or word == " " or word == "\n":
                continue
            try:
                wordvec.append(model.wv[str(word)])
            except KeyError as e:
                pass
        train_x.append(wordvec)
        rating = int(comment[1])
        if rating < 3:
            rating = 0
        elif rating == 3:
            rating = 1
        else:
            rating = 2
        train_y.append(rating)

        if i % 2000 == 0:
            print "已处理:百分之%s" % str(i * 100.0 / comment_size)

    return train_x, train_y


def get_train_data():
    comments = []
    print "正在获取训练数据"
    # 每种评论数据各取一万五千条
    for i in range(0, TRAIN_INDEX):
        comments.extend(get_bad_comments(i * 1000, 1000))

    for i in range(0, TRAIN_INDEX):
        comments.extend(get_middle_comments(i * 1000, 1000))

    for i in range(0, TRAIN_INDEX):
        comments.extend(get_good_comments(i * 1000, 1000))

    print "正在处理训练数据"
    return process_data(tflearn.data_utils.shuffle(comments)[0])


def get_test_data():
    comments = []
    print "正在获取测试数据"
    # 从一万五千条以后取数据
    for i in range(TRAIN_INDEX, TEST_INDEX):
        comments.extend(get_bad_comments(i * 1000, 1000))

    for i in range(TRAIN_INDEX, TEST_INDEX):
        comments.extend(get_middle_comments(i * 1000, 1000))

    for i in range(TRAIN_INDEX, TEST_INDEX):
        comments.extend(get_good_comments(i * 1000, 1000))

    print "正在处理测试数据"
    return process_data(tflearn.data_utils.shuffle(comments)[0])


def get_predict_origin_data():
    comments = []
    print "正在获取测试数据"
    # 从一万五千条以后取数据
    for i in range(TEST_INDEX, PREDICT_INDEX):
        comments.extend(get_bad_comments(i * 1000, 1000))

    for i in range(TEST_INDEX, PREDICT_INDEX):
        comments.extend(get_middle_comments(i * 1000, 1000))

    for i in range(TEST_INDEX, PREDICT_INDEX):
        comments.extend(get_good_comments(i * 1000, 1000))
    return comments


def get_predict_data(comments):
    print "正在处理测试数据"
    return process_data(comments)

