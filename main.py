"""

Title:          main.py

Description:    Script where all the modules are called. 
                Also the only interface between the user and the program.

"""

# ----- Imports -----
from modules import GetData, Descriptives, MovingAverage, ArimaForecast

## ----- Print Instructions -----
welcome = """
--------------------------------------------------
          FINANCIAL TECHNICAL ANALYSIS
--------------------------------------------------

"""

functionality = """
--------------------------------------------------
Functionalities: 

1 - Descriptive Statistics\n    Collection of descriptive statistics regarding the desired stock. \n
2 - Technical Analysis\n    Comparison of a buy-and-hold strategy with a technical analysis (bullish/bearish cross). \n
3 - Forecast\n    Prediction of return for the next days.\n
S - TYPE S TO CHANGE TICKERS
X - TYPE X TO QUIT THE PROGRAM.

--------------------------------------------------
"""

instructions = """
First, enter a ticker and  starting/ending dates.
Second, enter the functionality that you are interested in. 
"""

print(welcome)
input("Type ENTER to continue: \n > ")
print(instructions)


## ---- Ask the desired stock -----
data1 = GetData.get_stock()

## ----- Set the interface -----
prog = ''
while prog.upper() != "X" :
    # create a copy of the data set so unwelcome changes in the function do not matter
    data = data1.copy()
    # Ask the desired functionality
    print(functionality)
    prog = input("Enter the desired functionality:\n > ")
    
    # First Program 
    if prog == "1":
        print('List of descriptive statistics: ')
        Descriptives.descriptives(data)

    # Second Program
    elif prog == "2":
        print('Enter the orders of the moving averages.')
        print('Different values will return different gains/losses.')
        
        # Ask the inputs (also checks if input is integer and long > short)
        while True: 
            try:
                lag_short_term = int(input('Moving average order for short term:\n > '))
                lag_long_term = int(input('Moving average order for long term:\n > '))
            except ValueError:
                print('ERROR: You must enter an integer !')
                continue
            if lag_short_term >= lag_long_term: 
                print('ERROR: Short term order must be smaller than the long term order.')
            else: 
                break
        # Execute the moving-average analysis
        MovingAverage.move_av(data, lag_short_term, lag_long_term)
    
    # Third Program
    elif prog == "3":
        ArimaForecast.forecast(data)
            
    # New TICKER
    elif prog.upper() == "S":
        data1 = GetData.get_stock()
    
    # Warn the user that the program is finished
    if prog.upper() != "S":
        input("Functionality over. Press enter to return to the menu.")
