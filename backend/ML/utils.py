import numpy
import matplotlib.pyplot as plt
import math
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

scaler = MinMaxScaler(feature_range=(0, 1))
numpy.random.seed(7)


def look_back_dataset(dataset, look_back=1):
    """
      :param: dataset, look_back
      :return: trainX, trainY OR testX, testY
    """
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return numpy.array(dataX), numpy.array(dataY)



def normalize(dataset):
    """
        :param: dataset
        :return: dataset
    """
    dataset = scaler.fit_transform(dataset)
    return dataset


def split(dataset, dates):
    """
        :param: dataset, dates
        :return: train, test
    """
    train_size = int(len(dataset) * 0.67)
    test_size = len(dataset) - train_size
    train_y, test_y = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
    train_dates, test_dates = dates[0:train_size, :], dates[train_size:len(dates), :]
    return train_y, test_y, train_dates, test_dates


def reshape(trainX, testX):
    """
        reshape input to be [samples, time steps, features]

        :param: trainX, testX
        :return: trainX, testX
    """
    trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    return trainX, testX

def transform_predict(predict_Y):
    return scaler.inverse_transform(predict_Y)

def transform(Y):
    return scaler.inverse_transform([Y])



def rmse(Y, predict):
    """
        calculate root mean squared error

        :param: trainY, train_predict OR testY, test_predict
        :return: result
    """
    result = math.sqrt(mean_squared_error(Y[0], predict[:, 0]))
    return math.sqrt(mean_squared_error(Y[0], predict[:, 0]))


def plot(y, dates, train_predict, test_predict, look_back):
    """
        1. shift train predictions for plotting
        2. shift test predictions for plotting
        3. plot

        :param: y, train_predict, test_predict, look_back
        :return:
    """
    # 1.
    train_predict_plot = numpy.empty_like(y)
    train_predict_plot[:, :] = numpy.nan
    train_predict_plot[look_back:len(train_predict) + look_back, :] = train_predict

    # 2.
    test_predict_plot = numpy.empty_like(y)
    test_predict_plot[:, :] = numpy.nan
    test_predict_plot[len(train_predict) + (look_back * 2) + 1:len(y) - 1, :] = test_predict

    # 3.
    plt.plot(dates, scaler.inverse_transform(y))
    plt.plot(train_predict_plot)
    plt.plot(test_predict_plot)
    plt.show()
