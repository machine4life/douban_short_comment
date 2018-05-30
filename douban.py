# coding=utf-8
from douban_input import get_train_data, get_test_data
from tflearn.data_utils import to_categorical
import tflearn
import sys
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


def main():
    train_x, train_y = get_train_data()
    test_x, test_y = get_test_data()

    print "正在处理训练数据的 padding"
    train_x = pad_sequences_array(train_x, maxlen=100, value=0.)
    print "正在处理测试数据的 padding"
    test_x = pad_sequences_array(test_x, maxlen=100, value=0.)

    train_y = to_categorical(train_y, 3)
    test_y = to_categorical(test_y, 3)

    net = tflearn.input_data([None, 100, 200])
    net = tflearn.lstm(net, 128, dropout=0.8)
    net = tflearn.fully_connected(net, 3, activation='softmax')
    net = tflearn.regression(net, optimizer='adam', learning_rate=0.0001, loss='categorical_crossentropy')

    model = tflearn.DNN(net, tensorboard_verbose=1,
                        tensorboard_dir='log/', checkpoint_path='model/',
                        best_checkpoint_path='best_model/', best_val_accuracy=0.8)
    model.load("model-37000")
    model.fit(train_x, train_y, validation_set=(test_x, test_y),
              show_metric=True, batch_size=32,
              validation_batch_size=32, snapshot_step=500)
    model.save("model.tfl")


if __name__ == '__main__':
    main()
