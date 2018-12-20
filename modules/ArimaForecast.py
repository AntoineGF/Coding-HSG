import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy


def forecast(data):
    # running all the needed functions here and assign the data to variables
    test, train, days = data_prep(data)
    plotting(train)
    analysis(train)
    result, true_model = ARIMA_model_selection(train)
    ARIMA_forecast(result, test, train, true_model)
    return 0


def data_prep(data):
    # set the index to business month end frequency https://stackoverflow.com/a/35339226 fills missing values!!!!
    data = data.asfreq(freq="B", method='ffill')
    # create log returns
    data['logPrice'] = np.log(data['close'])
    data['logPrice'] = np.log(data['close'])
    data['logReturns'] = [None] * len(data)
    for n in range(1, len(data)):
        data.iloc[n, 2] = data.iloc[n, 1] - data.iloc[n - 1, 1]
    # deleting the columns that are not longer needed
    del data['logPrice']
    del data['close']
    # dropping missing values
    data.dropna(axis=0, inplace=True)
    # checking for correct input
    while True:
        try:
            days = int(input("How much days should the arima_forecast include? Minimum is 2\n> "))
            if days >= 2:
                break
        except ValueError:
            print("Wrong input, please insert an integer")
    # create a training and a test set
    train_size = int(len(data) * (len(data) - days) / len(data))
    train, test = data[0:train_size], data[train_size:len(data)]
    # asking the user about the highest order that should be tested
    return test, train, days


def plotting(train):
    train.plot()
    plt.show()
    # plot the autocorrelation function for the first 30 lags
    sm.tsa.graphics.plot_acf(train['logReturns'], lags=30, fft=True)
    plt.show()
    sm.tsa.graphics.plot_pacf(train['logReturns'], lags=30)
    plt.show()
    return 0


def analysis(train):
    # Augmented Dickey-Fuller unit root test
    stat = sm.tsa.stattools.adfuller(train['logReturns'], regression="nc", autolag='AIC', store=True)
    if stat[0] < stat[2]['5%']:
        print("The null hypthesis of the Augmented Dickey-Fuller unit root test, namely that the Series has a unit "
              "root, can be rejected at the 5 % level")

    return 0


def ARIMA_model_selection(train):
    while True:
        try:
            p = int(input("What is the maximum order the Arima should be tested for?\nPlease give p \n> "))
            i = int(input("Please give i\n> "))
            q = int(input("Please give q\n> "))
            max_order = [p, i, q]
            break
        except ValueError:
            print("Something went wrong. Please try again\n\n")
    min_order = [0, 0, 0]
    # testing an amount of ARIMA Models for the best
    result = pd.DataFrame(columns=["p", "i", "q", "BIC", "AIC", "error"])
    k = 0
    # going through every Arima model and save the key parameters
    for p in range(min_order[0], max_order[0] + 1):
        for i in range(min_order[1], max_order[1] + 1):
            for q in range(min_order[2], max_order[2] + 1):
                test_model = sm.tsa.ARIMA(np.asarray(train), (p, i, q))
                # accounting for models that have problems
                try:
                    res = test_model.fit(disp=0, trend="nc", method='css', transparams=True)
                    aic = res.aic
                    bic = res.bic
                    er = 0
                # if one of this two error occur, set the values and mark that the model does not work
                except (ValueError, np.linalg.LinAlgError):
                    bic = 0
                    aic = 0
                    er = 1
                # append the results to the result df
                result.loc[k] = [p, i, q, bic, aic, er]
                k += 1
    # convert data in the result dataFrame to float to avoid problems
    result = result.astype(float)
    print(result)
    # find the value with the lowest aic
    true_model = int(result.loc[result["error"] == 0]["AIC"].idxmin())
    return result, true_model


def ARIMA_forecast(result, test, train, true_model):
    # uses the best model according to the criterion and fits it again to obtain the result
    model = sm.tsa.ARIMA(np.asarray(train),
                         (int(result.p[true_model]), int(result.i[true_model]), int(result.q[true_model])))
    res = model.fit(disp=0, trend="nc", method='css', transparams=True)
    print(res.summary())
    # plot the residual
    plt.plot(res.resid)
    plt.show()

    # create a arima_forecast
    forecast = res.forecast(steps=len(test))
    forecast_w = pd.DataFrame(forecast[0], columns=["Forecast"])
    # compare arima_forecast to the real data
    diff = pd.concat([forecast_w.set_index(test.index), test], axis=1)
    diff.plot()
    plt.show()
    a = input("Do you want to perfom a step wise arima_forecast? (y/n)\nWARNING: Might take a long time depending "
              "on the amount of necessary forecasts\n\n> ")
    if a == "y":
        diff2 = test.copy(deep=True)
        # create a rolling forecast
        diff2['Forecast_r'] = copy.deepcopy(forecast[0])
        for ii in range(1, len(test)):
            train = train.append(test.iloc[ii - 1])
            model = sm.tsa.ARIMA(np.asarray(train),
                                 (int(result.p[true_model]), int(result.i[true_model]), int(result.q[true_model])))
            # trying to fit the model, if it fails, try another solver
            try:
                res = model.fit(disp=0, trend="nc", method='css', transparams=True)
            except ValueError:
                print("First solver failed")
                try:
                    res = model.fit(disp=0, trend="nc", solver='bfgs', method='css', transparams=True)
                except ValueError:
                    print("Second solver failed")
                    try:
                        res = model.fit(disp=0, trend="nc", solver='bfgs', method='css', transparams=True)
                    except ValueError:
                        print("Third solver failed")
                        try:
                            res = model.fit(disp=0, trend="nc", solver='newton', method='css', transparams=True)
                        except ValueError:
                            print("Fourth solver failed")
                            try:
                                res = model.fit(disp=0, trend="nc", solver='nm', method='css', transparams=True)
                            except ValueError:
                                print("Fifth solver failed")
                                try:
                                    res = model.fit(disp=0, trend="nc", solver='cg', method='css', transparams=True)
                                except ValueError:
                                    print("Sixth solver failed")
                                    try:
                                        res = model.fit(disp=0, trend="nc", solver='ncg', method='css',
                                                        transparams=True)
                                    except ValueError:
                                        print("Seventh solver failed")
                                        try:
                                            res = model.fit(disp=0, trend="nc", solver='powell', method='css',
                                                            transparams=True)
                                        except ValueError:
                                            print("Something went horrible wrong estimating the model. No solver finds"
                                                  " a solution")
                                            # if no solution is found, prediction becomes pointless, therefor return to
                                            # main function
                                            a = 0
                                            break
            forecast = res.forecast(steps=1)
            diff2['Forecast_r'][ii] = copy.deepcopy(forecast[0])
    if a == "y":
        diff2.plot()
        plt.show()

        # comparing the graphs graphically
        diff['Forecast'].plot()
        diff['logReturns'].plot()
        diff2['Forecast_r'].plot()

        plt.legend(['Forecast', 'Data', 'stepwise Forecast'])
        plt.show()

        # comparing the errors
        error = pd.DataFrame()
        error['Forecast'] = abs(diff['Forecast'] - diff['logReturns'])
        error['stepwise Forecast'] = abs(diff2['Forecast_r'] - diff2['logReturns'])
        print("The average prediction error for the first forecast is: ", error['Forecast'].mean(), "\n")
        print("The average prediction error for the second forecast is: ", error['stepwise Forecast'].mean(), "\n")

        # showing the difference graphically
        error['Forecast'].plot()
        error['stepwise Forecast'].plot()
        plt.legend(['Forecast error', 'stepwise Forecast error'])
        plt.show()
    else:
        # comparing the forecast with the realized values
        diff['Forecast'].plot()
        diff['logReturns'].plot()

        plt.legend(['Forecast', 'Data'])
        plt.tight_layout()
        plt.show()

        # comparing the errors
        diff['Error'] = abs(diff['Forecast'] - diff['logReturns'])
        print("The average prediction error for the first forecast is: ", diff['Error'].mean(), "\n")
    return 0
