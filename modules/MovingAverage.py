# Get the correct directory to work in
# filename = "/Users/antoinegex-fabry/Documents/Université/UNISG/3rd semester/Advanced Computer Programming/TechnicalAnalysis/temp"
# import os
# os.chdir(filename)

## ---- IMPORTS -----
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std


def move_av(data, lag_short_term, lag_long_term):
    # Compute log prices
    data['logPrice'] = np.log(data['close'])

    ## ---- GET THE OVERALL TREND ----

    # Here we perform a very simple OLS regression (price on time units)
    # We then plot the result of the estimation along with its confidence intervals

    # Prepare the data
    X = list(range(1, len(data) + 1))
    X = sm.add_constant(X)
    Y = list(data['close'])

    # OLS fit
    model = sm.OLS(Y, X).fit()

    # Get the statistics (no need to print it to the user as it's no useful info)
    # print(model.summary())
    

    # Function to have lower/upper bounds
    prstd, iv_l, iv_u = wls_prediction_std(model)

    # PLOT
    fig, ax = plt.subplots(figsize=(8, 6))
    x = list(range(1, len(data) + 1))
    y = data['close']
    ax.plot(x, y, 'b-', label="data")
    ax.plot(x, model.fittedvalues, 'r--.', label="OLS")
    ax.plot(x, iv_u, 'r--')
    ax.plot(x, iv_l, 'r--')
    ax.set_title('Price Evolution vs OLS')
    ax.legend(loc='best');

    print("\nGeneral trend of the time series:")
    plt.show()
    input("Press ENTER to continue:\n > ")

    ## ---- Compute and plot the Log returns  -----
    #  => r_t = ln(P_t) - ln(P_t-1)

    data['logPrice'] = np.log(data['close'])
    data['logReturns'] = [None] * len(data)

    for n in range(1, len(data)):
        data.iloc[n, 2] = data.iloc[n, 1] - data.iloc[n - 1, 1]

    # Get the average (in percent)
    averageReturn = np.round(np.mean(data['logReturns']), 5) * 100

    print("\nLog returns:")

    fig = plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    returns = plt.plot(data.reset_index().index, data['logReturns'])
    plt.setp(returns, color='red', linewidth=0.2)
    plt.plot(data.reset_index().index, [averageReturn / 100] * len(data), 'g')
    plt.xlabel("Periods")
    plt.legend(["Log Returns", 'Average Daily Returns: ' + str(averageReturn) + "%"], loc="best")
    plt.show()

    input("Press ENTER to continue:\n > ")

    ## ----- Moving average -----
    # Reference: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
    instr1 = """
    --------------------------------------------------
    
    Stock Price and its (equally weighted) moving averages    
    
    --------------------------------------------------
    """
    print(instr1)

    # Parameters and preparation
    length = len(data)
    ts = data['close']

    # Run the functions to compute simple (equally weighted) moving average
    ma_short = moving_average(ts, lag_short_term)
    ma_long = moving_average(ts, lag_long_term)

    fig = plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(data.index, data['close'], '-.')
    plt.plot(data.index, ma_short, '-r')
    plt.plot(data.index, ma_long, '-g')
    plt.legend(["Price", str(lag_short_term) + " days moving average", str(lag_long_term) + " days moving average"], loc="best")
    plt.xlabel("Date"), plt.ylabel("Stock Price"), plt.title("Equally weighted moving averages")
    plt.show()

    input("Press ENTER to continue:\n > ")

    print("Zooming-in to see the last 100 periods")

    fig = plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(data.index[(length - 100):length], data.iloc[(length - 100):length, 0], '-.')
    plt.plot(data.index[(length - 100):length], ma_short[(length - 100):length], '-r')
    plt.plot(data.index[(length - 100):length], ma_long[(length - 100):length], '-g')
    plt.legend(["Price", str(lag_short_term) + " days moving average", str(lag_long_term) + " days moving average"], loc="best")
    plt.xlabel("Date"), plt.ylabel("Stock Price"), plt.title("Last 100 periods")
    plt.show()

    
    input("Press ENTER to continue:\n > ")

    ## ----- Detect moments to buy/sell -----
    
    # BULLISH CROSSOVER
    instr2 = """
    --------------------------------------------------
    Potential gains/loss of BULLISH CROSSOVER strategy
    --------------------------------------------------
    
    Definition of the strategy:
    
    Buy:    short-term moving average > long-term moving average 
    Sell:   short-term moving average < long-term moving average
    
    """
    
    print(instr2)
    # Buy when ma_short > ma_long; sell when ma_short < ma_long
    ma = pd.DataFrame({'ma_short': ma_short, 'ma_long': ma_long, 'stockPrice': data['close']}).reset_index(drop="True")

    ma['change'] = ma['ma_short'] > ma['ma_long']
    ma['position'] = [None] * len(ma)
    
    # Call the function to compute the crossover return strategy
    gainsBH, gainsBullish = ma_crossover(ma, data)

    input("Press ENTER to continue:\n > ")

    # BEARISH CROSSOVER
    instr3 = """
    --------------------------------------------------
    Potential gains/loss of BEARISH CROSSOVER strategy
    --------------------------------------------------
    
    Definition of the strategy:
    
    Buy:    short-term moving average < long-term moving average 
    Sell:   short-term moving average > long-term moving average
    
    """
    
    print(instr3)
    
    # Buy when ma_short < ma_long; sell when ma_short > ma_long
    ma = pd.DataFrame({'ma_short': ma_short, 'ma_long': ma_long, 'stockPrice': data['close']}).reset_index(drop="True")

    ma['change'] = ma['ma_short'] < ma['ma_long']
    ma['position'] = [None] * len(ma)
    
    # Call the function to compute the crossover return strategy
    gainsBH, gainsBearish = ma_crossover(ma, data)

    # Determine which was the best strategy
    if (gainsBH > gainsBullish) and (gainsBH > gainsBearish):
        print("Buy-and-hold was the best strategy !")
    elif gainsBearish > gainsBullish:
        print("Bearish cross was the best strategy !")
    else:
        print("Bullish cross was the best strategy")

    return 0


## ----- TECHNICAL ANALYSIS -----

# Equally Weighted Moving Average
def moving_average(ts, lags):
    # Inputs
    # ts:       time series that we want to take the moving average from
    # lags:     depends on user inputs
    # return:   ma, the moving average series

    # Define length + intialize ma vector
    length = len(ts)
    ma = [None] * length

    # defines the equally weighted coefficients
    coeff = np.ones(int(lags)) / float(lags)

    for i in range(lags, length):
        # Gets the previous ith lags and computes the moving average iteratively
        temp = list(ts.iloc[list(range(i - lags, i))]) * coeff
        ma[i] = sum(temp)

    return ma

# Exponentially weighted moving average (UNUSED)
def EWMA(ts, theta):
    length = len(ts)
    ewma = [None] * length
    ewma[0] = ts.iloc[0]
    for i in range(1, length):
        ewma[i] = theta * ts.iloc[i] + (1 - theta) * ewma[i - 1]

    return ewma


def ma_crossover(ma, data):
    # Gets the first occurence when the condition is True (depends on bearish/bullish)
    pos = ma.index[(ma.change == True)][0]

    # Check when moving averages cross one another
    for n in range(pos, len(ma)):
        # Compare consecutive values of True / False
        if ma.iloc[n, 3] != ma.iloc[n - 1, 3]:
            # If the value is true -> ma_short > ma_long so we should buy / Otherwise, sell
            if ma.iloc[n, 3]:
                ma.iloc[n, 4] = "Buy"
            else:
                ma.iloc[n, 4] = "Sell"
        # If the ma do not cross, we simply hold our position
        else:
            ma.iloc[n, 4] = "Hold"

    # Not very elegant but working
    payoff = ma.loc[(ma['position'] == "Buy") | (ma['position'] == "Sell"), ['stockPrice', 'position']]
    payoff = payoff.pivot(columns="position", values="stockPrice")
    buyPayoff = payoff['Buy'].dropna().reset_index(drop="True")
    sellPayoff = payoff['Sell'].dropna().reset_index(drop="True")

    # We have a nice matrix that allows us to compute the payoffs at each transaction
    # (ignoring transaction costs)
    payoff = pd.DataFrame({"Buy": buyPayoff, "Sell": sellPayoff})
    payoff['payoff'] = payoff['Sell'] - payoff['Buy']

    print("Transactions scheme:\n")
    print(payoff)
    input("\nPress ENTER to continue:\n > ")

    ## ---- Finally compute the absolute/relative payoffs -----
    # Absolute payoffs
    # Note that for Buy&Hold (=gainsBH), it starts when the first MA stock is bought (otherwise, unfair)
    gainsBH = data['close'][len(data) - 1] - data['close'][pos]
    gainsMA = sum(payoff['payoff'].dropna())

    # Distinguish between gains / loss
    if gainsBH > 0:
        print("Gains in $ from the technical analysis strategy: " + str(gainsMA) + "$")
        print("Gains in $ from a simple buy-and-hold strategy: " + str(gainsBH) + "$")
        print("Is the technical analysis worth it ?")
        print(" > " + str(gainsMA > gainsBH))

        # Relative payoffs
        print("\nIn relative terms:\n")
        print("MA relative gains: " + str(np.round(100 * gainsMA / data['close'][0], 3)) + "%")
        print("B&H relative gains: " + str(np.round(100 * gainsBH / data['close'][0], 3)) + "%\n")
    else:
        print("Loss in $ from the technical analysis strategy: " + str(gainsMA) + "$")
        print("Loss in $ from a simple buy-and-hold strategy: " + str(gainsBH) + "$")
        print("Is the technical analysis worth it ?")
        print(" > " + str(gainsMA > gainsBH))

        # Relative payoffs
        print("\nIn relative terms:\n")
        print("MA relative gains: " + str(np.round(100 * gainsMA / data['close'][0], 3)) + "%")
        print("B&H relative gains: " + str(np.round(100 * gainsBH / data['close'][0], 3)) + "%\n")

    # Note that the B&H gains might be different from the two strategies.
    # This is because we consider the start of the B&H strategy at the same date as the first trade is made in
    #      the respective strategy.

    return gainsBH, gainsMA
