'''

11.09.2018 - Function to get the data from quandl, using the user's inputs

Only argument is the user's own API.

'''

# IMPORTS
import quandl
import datetime as dt
import pandas as pd
import os.path
import configparser as cf
from alpha_vantage.timeseries import TimeSeries


def get_stock():
    ## ---- CONFIGURATION ----
    # read the config file
    config = cf.ConfigParser()
    config.read("config.ini")

    # get the values from the config file
    path = config['Dataloading']['filename']
    save = config['Dataloading']['save']
    filename = config['Dataloading']['save_filename']
    load = config['Dataloading']['load']
    # checks if data should be downloaded from quandl
    # print(load)
    if load == "1" or load == "2":
        # checks if file with api_key does exist
        if os.path.isfile("API_Key/api_key.txt"):
            f = open("API_Key/api_key.txt", "r")
            userAPI_1 = f.read()

            # two keys are needed, if this does not work, asks for two keys and overwrites the file
            try:
                userAPI, alpha = userAPI_1.split(sep=",")
                f.close()
            except ValueError:
                # the file should still be open in read mode, so it should be closed first
                f.close()

                # open the file in write mode
                f = open("API_Key/api_key.txt", "w+")
                print("At least one key was not found\n")
                userAPI = input("Please insert your key for Quandl\n> ")
                alpha = input("Please insert your key for alphavantage\n> ")

                # combine the keys to one string, separated by a comma and save it to a file
                keys = userAPI + "," + alpha
                f.write(keys)
                f.close()
        # if file does not exist, ask user for the key and save the key to a text file
        else:
            userAPI = input("> Please insert a valid API key for Quandl\n> ")
            alpha = input("> Please insert a valid API key for alphavantage\n> ")
            # checks if the needed directory exist
            if not os.path.isdir("API_Key"):
                # creates the directory if it does not exist
                os.mkdir("API_Key")

            f = open("API_Key/api_key.txt", "w")
            # creates a variable with the two keys, separated and saves it to a file
            keys = userAPI + "," + alpha
            f.write(keys)
            f.close()
        # Set up Quandl
        quandl.ApiConfig.api_key = userAPI

        # ---- INPUTS -----
        ticker = str(input("Please enter a Ticker:\n> "))
        # while loop runs until a correct start and end date is inserted
        while True:
            try:
                print("Enter the required dates using the following format: 'dd/mm/YYYY'")
                start = str(input("Starting date:\n> "))
                end = str(
                    input("Ending date. For today's day, please type 'today':\n> "))

                # Check the validity of the inputs
                # Checks if the start/end have a / element + if length of each element is ok

                print("Thanks, we are procedding your inputs...\n")

                # Transfrom into date objects
                start = dt.datetime.strptime(start, "%d/%m/%Y")
                if end == "today":
                    end = dt.datetime.today()
                else:
                    end = dt.datetime.strptime(end, "%d/%m/%Y")
                break
            except ValueError:
                print("You entered a wrong time. Please try again \n")

        print("Selected ticker: " + str(ticker))
        print("Starting date is: " + str(start))
        print("Ending date is: " + str(end) + "\n")

        # ---- Get the Data ----
        if load == "1":
            data = quandl.get_table('WIKI/PRICES', ticker=ticker,
                                    qopts={'columns': ['ticker', 'date', 'adj_close']},
                                    date={'gte': start, 'lte': end},
                                    paginate=True)
            # Turn the data into a Pandas DataFrame
            data = pd.DataFrame(data)
            # saves the file if user wants it
            if save == "1":
                data.to_csv("data/" + filename + ".txt")

            print("Here's what the data look like:\n")
            print(data.head())

            # Set the date as index
            data = data.set_index('date')
            del data['ticker']
            # Rename the column 
            data.columns.values[0] = 'close'
            
        # loads the file from the local directory if user wants it
        elif load == "2":
            data1 = TimeSeries(key=alpha, output_format='pandas')
            data1, waste = data1.get_daily_adjusted(symbol=ticker, outputsize='full')
            data = pd.DataFrame(columns=['close'])
            data['close'] = data1['5. adjusted close']
            # from https://stackoverflow.com/a/40815950
            data.index = pd.to_datetime(data.index)
        
            # saves the file if user wants it
            if save == "1":
                data.to_csv("data/" + filename + ".txt")
                
            # Select starting and ending dates
            data = data.loc[(data.index >= start) & (data.index <= end), :]
            print(data.head())

    else:
        data = pd.read_csv("data/" + path + ".txt")
        data = pd.DataFrame(data)
        # tires to delete None column
        try:
            del data['None']
        except KeyError:
            pass
        # converts date to datetime
        data['date'] = pd.to_datetime(data['date'])

        print("Here's what the data look like:\n")
        print(data.head())

        # Set the date as index
        data = data.set_index('date')
        # deletes ticker column if existing
        try:
            del data['ticker']
        except KeyError:
            pass

    # Sort from old to new
    data = data.sort_index()
    
    # print("\n With date as index")
    # print(data.info())

    # ---- CONTROLS ----
    # Controlling for data size 
    # If too small, poor forecasts and problems with Moving averages 
    # Not able to compute 35 days moving average for example
    if len(data) <= 250: 
        print('ATTENTION: small amount of data points might cause problems to the moving average computations.')
    

    # ---- RETURN  ----
    return data
