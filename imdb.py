# coding=utf-8

from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from tflearn.datasets import imdb


def main():
    # load IMDB Dataset

    train, test, _ = imdb.load_data(path='imdb.pkl', n_words=10000)

    trainX, trainY = train
    testX, testY = test

    print (len(trainX))
    print (len(trainX[0]))


    # Data preprocesssing
    # Sequence padding
    trainX = pad_sequences(trainX, maxlen=100, value=0.)
    testX = pad_sequences(testX, maxlen=100, value=0.)

    # Coverting labels to binary vectors
    trainY = to_categorical(trainY, nb_classes=2)
    testY = to_categorical(testY, nb_classes=2)

    for i in range(0, 20):
        print (trainX[i])

    for i in range(0, 20):
        print (trainY[i])

    # network building
    net = tflearn.input_data([None, 100])
    net = tflearn.embedding(net, input_dim=10000, output_dim=128)
    net = tflearn.lstm(net, 128, dropout=0.8)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    net = tflearn.regression(net, optimizer='adam', learning_rate=0.001, loss='categorical_crossentropy')

    # Training
    model = tflearn.DNN(net, tensorboard_verbose=0)
    model.fit(trainX, trainY, validation_set=(testX, testY), show_metric=True, batch_size=32)

if __name__ == '__main__':
    main()
