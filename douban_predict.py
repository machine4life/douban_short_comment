# coding=utf-8
from douban_input import get_predict_origin_data, get_predict_data
from tflearn.data_utils import to_categorical
import tflearn
import sys
import csv
import codecs
reload(sys)
sys.setdefaultencoding("utf-8")
import numpy as np


def pad_sequences_array(sequences, maxlen=None, dtype='float64', padding='post',
                  truncating='post', value=0.):
    """ pad_sequences.

    Pad each sequence to the same length: the length of the longest sequence.
    If maxlen is provided, any sequence longer than maxlen is truncated to
    maxlen. Truncation happens off either the beginning or the end (default)
    of the sequence. Supports pre-padding and post-padding (default).

    Arguments:
        sequences: list of lists where each element is a sequence.
        maxlen: int, maximum length.
        dtype: type to cast the resulting sequence.
        padding: 'pre' or 'post', pad either before or after each sequence.
        truncating: 'pre' or 'post', remove values from sequences larger than
            maxlen either in the beginning or in the end of the sequence
        value: float, value to pad the sequences to the desired value.

    Returns:
        x: `numpy array` with dimensions (number_of_sequences, maxlen)

    Credits: From Keras `pad_sequences` function.
    """
    lengths = [len(s) for s in sequences]

    nb_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    x = (np.ones((nb_samples, maxlen, 200)) * value).astype(dtype)
    for idx, s in enumerate(sequences):
        if len(s) == 0:
            continue  # empty list was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError("Truncating type '%s' not understood" % padding)

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError("Padding type '%s' not understood" % padding)
    return x


def get_predict_y(p_y):
    index = 0
    m = 0.
    for i in range(0, len(p_y)):
        if m < p_y[i]:
            index = i
            m = p_y[i]
    return index


def main():
    o_c = get_predict_origin_data()
    p_x, p_y = get_predict_data(o_c)

    print "正在处理预测数据的 padding"
    p_x = pad_sequences_array(p_x, maxlen=100, value=0.)

    p_y = to_categorical(p_y, 3)

    net = tflearn.input_data([None, 100, 200])
    net = tflearn.lstm(net, 128, dropout=0.8)
    net = tflearn.fully_connected(net, 3, activation='softmax')
    net = tflearn.regression(net, optimizer='adam', learning_rate=0.001, loss='categorical_crossentropy')

    model = tflearn.DNN(net, tensorboard_verbose=1,
                        tensorboard_dir='log/', checkpoint_path='model/',
                        best_checkpoint_path='best_model/', best_val_accuracy=0.9)
    model.load("model-37000")
    r = model.predict(p_x)
    save_as_csv(r, o_c)


def save_as_csv(r, comments):
    with open("predict.csv", 'wb') as f:
        f.write(codecs.BOM_UTF8)
        writer = csv.writer(f)
        writer.writerow(["content", "rating", "predict_rating"])
        for i in range(0, len(comments)):

            rating = int(comments[i][1])
            if rating < 3:
                rating = 0
            elif rating == 3:
                rating = 1
            else:
                rating = 2

            writer.writerow([comments[i][0], rating, get_predict_y(r[i])])


def test():
    print get_predict_y([0.001, 0.002, 0.003]), 3
    print get_predict_y([0.003, 0.002, 0.001]), 1
    print get_predict_y([0.002, 0.003, 0.001]), 2


if __name__ == '__main__':
    main()
