# Coding-HSG---Technical-Analysis

**Authors**: Tobias Bolter, Antoine Gex-Fabry, Ludovic Tuchschmid

## Goals

This work is done on academic purposes at the University of St.Gallen (HSG).

Objectives of the project:
The objective is to get familiar with Python and to develop a program that reads
the user's input and returns financial information about a stock price.

The program has three main functionalities (more details below):
1. **Descriptive statistics**: provides the user with 10 fundamental pieces of information.
That is, the first four moments (mean, variance, skewness, kurtosis), the evolution of the stock price,
its (log) returns, QQ-plots for normal and student distributions, the Value-at-risk
and the expected shortfall.
2. **Technical Analysis**: compares the returns (in percentage and in dollar terms)
of three different strategies based on momentum. The benchmark strategy is a simple
buy-and-hold, consisting of buying the stock in the first period and selling it in the last one.
This benchmark is compared to bullish and bearish cross. Those two strategies are based on the
comparison between short and long moving average (buy and sell orders are triggered when
the short moving average goes above/below the long moving average).
3. **Forecasts**: Lets the user define a training and a test set. The training set is assumed to be known from
the beginning, while the test set is treated as unknown and used to compare the forecast to real values.
ACF and PACF functions are plotted so the user might determine reasonable maximum values for the ARIMA model.
An augmented Dickey-Fuller test is performed to check if there is a unit root. Then the program tries to find
the best ARIMA model based on the AIC. Afterwards the user has to possibility to perform a stepwise forecast.
In this case, the ARIMA model is used to forecast the next period. Then the true value of the next period
gets added to the model and the ARIMA model gets reestimated, than the forecast for the period t+2 is performed.
This goes until the last period of the test set is reached. Afterwards the different forecasts are compared
 with the true values

## Instructions

### How the code is structured

The program must be run from `main.py` with CPython 3.6 (3.7 should also work).
The libraries needed to run the program are listed in the libraries.txt. file.
Please make sure that all the needed libraries are installed with the correct version, otherwise problems
might occur.

All the functionalities are written as functions and saved under the folder _modules_.

GIFs are also included to help the understanding.

### Before running the application

#### API keys
It is required that the user has an API key for Quandl **and** for Alphavantage.
Please do the necessary steps to get those requirements from the website of the data providers.
Here are the <a href = "https://docs.quandl.com/docs/python-installation"  target="_blank">instructions for Quandl</a> and here are the <a href = "https://www.alphavantage.co/support/#api-key" target="_blank">instructions for Alphavantage</a>.

Those two API keys will only be asked from the user the first time she/he runs the program.
They will then be stored in a text file and saved in `API_Key` folder to be called for the next times.

#### Configuration (config.ini)

The file `config.ini` contains the general settings for this application.
These includes:
  * save: Whether the dataset should be saved as a csv file locally. Default value: `0`.
  * load: Which data provider to use: `0` loads a local dataset, `1` uses Quandl, `2` uses Alphavantage. Default value: `1`.
  * filename: If `load = 0`, filename of the dataset to be loaded.
  * save_filename: If `save = 1`, this is the name given to the saved file. Default value: new.



If the dataset is saved, it will go in the folder `data`.

###  User inputs

On the **application level**, the initial inputs are:
  * Ticker
  * Start/End dates for the data

![](/gifs/LoadData.gif)

List of available tickers:
<a href = "https://www.quandl.com/data/EOD-End-of-Day-US-Stock-Prices"  target="_blank">Quandl Website</a>

**Descriptive statistics:**
  * An integer between 1 and 9 to access various descriptives statistics (X to quit)

![](/gifs/Descriptives.gif)


**Technical analysis:**
  * Lags for short-term moving average
  * Lags for long-term moving average

![](/gifs/MovingAverage.gif)


**Forecast:**
  * Number of days to forecast (minimum 2)
  * Orders of the ARIMA process (p, i, q)
  * Performance of a stepwise forecast ('y' performs it, all other values continue without it)


![](/gifs/Forecast.gif)


### Outputs
  - Graphs of time series stock price and returns
  - Different technical analysis techniques, along with their graphs and their realized historical returns on the period
  - Forecasting and evaluation

### Known Warnings produced by Python (can be ignored):
  - FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated; use `arr[tuple(seq)]` instead of `arr[seq]`. In the future this will be interpreted as an array index, `arr[np.array(seq)]`, which will result either in an error or a different result.
    zf = out_full[ind]
    caused by statsmodels, see https://github.com/statsmodels/statsmodels/issues/4821,
  - SettingWithCopyWarning:
    A value is trying to be set on a copy of a slice from a DataFrame
    See the caveats in the documentation: http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy
    diff2['Forecast_r'][ii] = copy.deepcopy(forecast[0])
