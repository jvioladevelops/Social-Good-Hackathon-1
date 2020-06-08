import os
import time
import numpy as np
import datetime as dt
from matplotlib import pyplot as plt
from tensorflow import keras
from werkzeug.exceptions import abort

# TODO save dependencies to requirements.txt
# TODO update docstrings
from backend.ML.utils import load_data, preprocess, filter_by_country, \
    separate, normalize, apply_lookback, reshape, unite_dates_samples, \
    denormalize, append_sample, change_date, DATE_FORMAT


class RNN:
    def __init__(self, country_code, look_forward=3):
        """
        """
        if not country_code:
            abort(422)

        self.look_back = look_forward
        self.look_forward = look_forward + 1
        self.country_code = country_code
        self.models_src = f'{os.path.dirname(__file__)}/models_countries'
        self.model = keras.models.load_model(
            f'{self.models_src}/{self.country_code}-RNN.h5')

    def predict(self, requested_day):
        """
        """
        # TODO tests

        # TODO refactor: get data from database
        df = load_data()

        # preprocess
        df = preprocess(df)
        df = filter_by_country(df, self.country_code)

        # separate cases from data
        dates, Y = separate(df)

        # normalize Y
        Y = normalize(Y)

        # apply look_back and generate needed samples
        X, _ = apply_lookback(Y, look_back=self.look_back)

        # reshape to fit the model
        X = reshape(X)
        dates = reshape(dates)
        dates = dates[self.look_back:]

        # unite with dates, consider
        united_samples = unite_dates_samples(dates.reshape(-1, 1),
                                             X.reshape(-1, self.look_back))

        last_day = requested_day
        predicted = 0

        for step in range(self.look_forward):
            sample, last_day = self.get_sample(united_samples, last_day)
            sample = sample.reshape(1, 1, self.look_back)

            # make predictions one step further
            predicted = self.model.predict(sample.astype(np.float32))

            united_samples, last_day = append_sample(united_samples, predicted,
                                                     self.look_back,
                                                     last_day, step)

        last_day = dt.datetime.strptime(last_day, DATE_FORMAT)
        last_day = change_date(last_day, delta_days=-1)
        last_day = dt.datetime.strftime(last_day, DATE_FORMAT)

        predicted = denormalize(predicted)[0, 0]
        predicted = int(predicted)
        message = f'On {last_day} expect the number of new cases ' \
            f'to be equal {predicted} '

        return predicted, message

    def get_trend(self, day):
        """
        """
        predicted, _ = self.predict(day)

        # TODO implement increasing/decreasing trend after predictions are
        #  implemented
        trend = None

        return trend

    def get_sample(self, united_samples, day):
        """
            Takes self.lookback days behind and the corresponding new cases of
            COVID-19.

        """
        search_res = np.where(united_samples[:, 0] == day)[0]
        if len(search_res) == 0:
            sample = united_samples[-1:, :]
            day_taken = sample[0, 0]
        else:
            sample = united_samples[united_samples[:, 0] == day]
            day_taken = day

        sample = sample[0, 1:]  # eliminate date in the first column
        return sample, day_taken
