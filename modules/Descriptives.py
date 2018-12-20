import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import scipy.stats as stats
from tabulate import tabulate
import pylab
import seaborn as sns

# List Descriptives:
#   1: Price Time Serie
#   2: Returns Time Serie
#   3: Returns Distribution
#   4: Returns QQ Plot Normal
#   5: Returns QQ Plot Student-t
#   6: VaR Normal
#   7: VaR Empirical
#   8: ES Normal
#   9: ES Empirical
#  10: Summary Stats Table

def descriptives(data):
    """
    A function to access various descriptive statistics from the list:
     1: Price Time Serie
     2: Returns Time Serie
     3: Returns Distributions
     4: Returns QQ Plot Normal
     5: Returns QQ Plot Student-t
     6: VaR Normal
     7: VaR Empirical
     8: ES Normal
     9: ES Empirical
     10: Summary Stats Table

    Input: Any dataset with date set as index
    Output: Various graphs and tables
    """
    data['logReturns'] = np.log(data['close']) - np.log(data['close'].shift(periods=1))

    A = 0
    while A != 'x' or A != 'X':
        print('\n 1: Price Time Serie \n 2: Returns Time Serie \n 3: Returns Distributions \n 4: Returns QQ Plot Normal \n 5: Returns QQ Plot Student-t \n 6: VaR Normal \n 7: VaR Empirical \n 8: ES Normal \n 9: Summary statistics table \n\n Press X to exit')
        A = (input('Enter a number for the stat from the list above: '))       
                
        if A == '1':
        #   1: Price Time Serie
            print('\n \n Here is the time serie of the stock price: \n \n ')    
            fig, ax = plt.subplots(1)
            ax.plot(data.index, data['close'], label='Close Price')
            
            # format the ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
            fig.autofmt_xdate()
            pylab.legend(loc='upper left')
            plt.show()
            continue

        elif A == '2':
        #   2: Returns Time Serie
            print('\n \n Here is the time serie of the stock return: \n \n ')    
            fig, ax = plt.subplots(1)
            ax.plot(data.index, data['logReturns'], label='Log returns')
            
            # format the ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
            fig.autofmt_xdate()
            pylab.legend(loc='upper left')
            plt.show()
            continue

        elif A == '3':
        #   3: Returns Histogram
            print('\n \n Here is a histogram of the stock return: \n \n ')    
            fig, ax = plt.subplots(1)
            sns.distplot(data['logReturns'].dropna(), hist=False, kde=True, 
                         kde_kws = {'shade': False, 'linewidth': 2}, 
                         bins=int(180/5), color = 'darkblue',
                         label = 'Empirical distribution')
            
            # Normal distribution fit
            mu, sigma = stats.norm.fit(data['logReturns'].dropna(), label='Log returns')
            xmin, xmax = plt.xlim()
            x1 = np.linspace(xmin, xmax, 200)
            p = stats.norm.pdf(x1, mu, sigma)
            sns.lineplot(x1, p,  
                         color = 'red',
                         label = 'Normal distribution')
            plt.show()
            continue
        
        elif A == '4':
        #   4: Returns QQ Plot Normal
            print('\n \n Here is the normal QQ-plot of the stock return: \n \n ')    
            fig, ax = plt.subplots(1)
            plot = stats.probplot(data['logReturns'].dropna(), dist='norm', plot=pylab)
            ax.set_title("Probplot for normal dist")
            plt.show()
            continue
        
        elif A == '5':
        #   5: Returns QQ Plot Student-t
            print('\n \n Here is the Student-t QQ-plot of the stock return: \n \n ')    
            fig, ax = plt.subplots(1)
            plot = stats.probplot(data['logReturns'].dropna(), dist='t', sparams=(3), plot=pylab)
            ax.set_title("Probplot for t dist with df = 3")
            plt.show()
            continue            

        elif A == '6':
        #   6: VaR Normal
            print('\n \n Here is the value at risk of the stock return: \n \n ')    
            mean, std = stats.norm.fit(data['logReturns'].dropna(), label='Log returns')
            VaR_90 = stats.norm.ppf(1-0.9, mean, std)
            VaR_95 = stats.norm.ppf(1-0.95, mean, std)
            VaR_99 = stats.norm.ppf(1-0.99, mean, std)
            print(tabulate([['90%', VaR_90], ['95%', VaR_95], ['99%', VaR_99]], headers=["Confidence Level", "Value at Risk"]))
            continue
        
        elif A == '7':
        #   7: VaR Empirical
            print('\n \n Here is the empirical value at risk of the stock return: \n \n ')    
            #data.sort_values('logReturns', inplace=False, ascending=True)
            VaR_90 = data['logReturns'].quantile(0.1)
            VaR_95 = data['logReturns'].quantile(0.05)
            VaR_99 = data['logReturns'].quantile(0.01)
            print(tabulate([['90%', VaR_90], ['95%', VaR_95], ['99%', VaR_99]], headers=["Confidence Level", "Empirical value at Risk"]))
            continue
        
        elif A == '8':
        #   8: ES Normal    
            print('\n \n Here is the expected shortfall of the stock return: \n \n ')    
            mean, std = stats.norm.fit(data['logReturns'].dropna(), label='Log returns')
            CVaR_90 = -stats.norm.pdf(stats.norm.ppf(0.1))*1/0.1*std - mean
            CVaR_95 = -stats.norm.pdf(stats.norm.ppf(0.05))*1/0.05*std - mean
            CVaR_99 = -stats.norm.pdf(stats.norm.ppf(0.01))*1/0.01*std - mean            
            print(tabulate([['90%', CVaR_90], ['95%', CVaR_95], ['99%', CVaR_99]], headers=["Confidence Level", "Expected shortfall"]))
            continue

        elif A == '9':        
        #   10: Summary Stats Table
            print('\n \n Here is the table with summary statistics of the stock return: \n \n ')    
            Emp_VaR_90 = data['logReturns'].quantile(0.1)
            Emp_CVaR_90 = np.mean(data[data.logReturns <= Emp_VaR_90]['logReturns'])
            Emp_VaR_95 = data['logReturns'].quantile(0.05)
            Emp_CVaR_95 = np.mean(data[data.logReturns <= Emp_VaR_95]['logReturns'])
            Emp_VaR_99 = data['logReturns'].quantile(0.01)
            Emp_CVaR_99 = np.mean(data[data.logReturns <= Emp_VaR_99]['logReturns'])
            print(tabulate([['90%', Emp_CVaR_90], ['95%', Emp_CVaR_95], ['99%', Emp_CVaR_99]], headers=["Confidence Level", "Expected shortfall"]))
            continue
        
        elif A == '10':        
        #   10: Summary Stats Table
            print('\n \n Here is the table with summary statistics of the stock return: \n \n ')    
            mu = np.mean(data['logReturns'].dropna())
            sigma = np.std(data['logReturns'].dropna())
            skew = stats.skew(data['logReturns'].dropna())
            kurt = stats.kurtosis(data['logReturns'].dropna())
            print(tabulate([['Mean', mu], ['Std', sigma], ['Skewness', skew], ['Kurtosis', kurt]], headers=["Statistic", "Value"])) 
            continue
        
        elif A.upper() == 'X':
            break

        else:
            print('\n ERROR - Use a number from the list or type "x" to exit')
