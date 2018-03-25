"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
from util import get_data, plot_data

def compute_portvals(orders_file = "./results_df.csv", start_val = 10000):

    order_data = pd.read_csv(orders_file)
    order_data = order_data.sort_values(['Date'])

    order_start_date = order_data['Date'][0]
    order_end_date = order_data['Date'][len(order_data)-1]

    start_date = dt.datetime(int(order_start_date[0:4]), int(order_start_date[5:7]), int(order_start_date[8:10]))
    end_date = dt.datetime(int(order_end_date[0:4]), int(order_end_date[5:7]), int(order_end_date[8:10]))

    symbols = np.unique(order_data['Symbol'])
    symbols = symbols.tolist()

    portvals = get_data(symbols, pd.date_range(start_date, end_date))
    portvals = portvals[symbols]

    # Initialize zeros for allocations dataframe
    initialize_zeros = np.zeros(shape=(len(portvals),len(symbols)))
    alloced_val = pd.DataFrame(initialize_zeros, index = portvals.index, columns=[symbols])

    # Initialize zeros for cash dataframe
    initialize_cash_zeros = np.zeros(shape=(len(portvals),1))
    cash_val = pd.DataFrame(initialize_cash_zeros, index = portvals.index, columns=['CASH'])
    cash_val['CASH'][0] = start_val

    # Insert trades and subtract or add cash
    for index, row in order_data.iterrows():
        current_order_data = get_data([row['Symbol']], pd.date_range(row['Date'], row['Date']))
        current_order_val = current_order_data[row['Symbol']]*row['Shares']
        current_shares = row['Shares']
        if row['Order'] == "BUY":
            alloced_val.loc[row['Date']][row['Symbol']] = alloced_val.loc[row['Date']][row['Symbol']] + current_shares
            cash_val.loc[row['Date']]['CASH'] = cash_val.loc[row['Date']]['CASH'] - current_order_val[0]
        elif row['Order'] == "SELL":
            alloced_val.loc[row['Date']][row['Symbol']] = alloced_val.loc[row['Date']][row['Symbol']] - current_shares
            cash_val.loc[row['Date']]['CASH'] = cash_val.loc[row['Date']]['CASH'] + current_order_val[0]

    alloced_val = alloced_val.cumsum()
    cash_val = cash_val.cumsum()

    # Multiply share price with number of shares
    alloced_val = pd.DataFrame(alloced_val.values*portvals.values, columns=alloced_val.columns, index=alloced_val.index)

    # combine allocations and cash df
    portvals = pd.concat([alloced_val, cash_val], axis=1)
    print(portvals)

    # sum over each row for portoflio value of that day
    portvals = portvals.sum(axis=1)
    return portvals

def compute_portfolio_stats(prices,  allocs=[0.1,0.2,0.3,0.4], rfr = 0.0, sf = 252.0):
    # Cumulative Return
    cr = prices.ix[-1]/prices.ix[0] - 1

    # Average Daily Return
    daily_returns = prices.copy()
    daily_returns.ix[1:] = (prices.ix[1:]/prices.ix[:-1].values) - 1
    daily_returns.ix[0] = 0
    adr = daily_returns.ix[1:].mean(index=0)

    # stdev Daily Return
    sddr = daily_returns.ix[1:].std(index=0)

    # Sharpe Ratio
    s = daily_returns - rfr
    sr = np.sqrt(sf)*(s.ix[1:].mean(index=0)/sddr)

    return cr, adr, sddr, sr


def test_code():
    # Define input parameters

    of = "./results_df.csv"
    sv = 10000

    # Process orders
    portvals = compute_portvals(orders_file = of, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"
    portvals.plot()
    plt.show()

    # Read in adjusted closing prices for SPY
    dates = pd.date_range(dt.datetime(2007,12,29), dt.datetime(2009,12,29))
    prices_SPY = get_data(['$SPX'], dates)  # automatically adds SPY

    # Normalize
    norm_port_val = portvals/portvals.ix[0, :]
    norm_SPY = prices_SPY/prices_SPY.ix[0, :]

    # Compare daily portfolio value with SPY using a normalized plot
    plt.plot(norm_port_val, label='Portfolio')
    plt.plot(norm_SPY, label='$SPX')
    plt.legend(loc='upper left')
    plt.title("2009-2011 IBM Portfolio Value vs $SPX")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()

    # Get portfolio stats
    start_date = dt.datetime(2007,2,28)
    end_date = dt.datetime(2009,12,31)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = cr, adr, sddr, sr =  compute_portfolio_stats(portvals,  allocs=[0], rfr = 0.0, sf = 252.0)
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY =  compute_portfolio_stats(prices_SPY,  allocs=[0.1,0.2,0.3,0.4], rfr = 0.0, sf = 252.0)

    # Compare portfolio against $SPX
    print "Date Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

if __name__ == "__main__":
    test_code()
