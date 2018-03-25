__author__ = 'Raymond Yeh'


import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import marketsim
import LinReg_stock_learner
import bollinger_strategy


def test_run():
    # Read data
    # dates = pd.date_range('2009-12-31', '2011-12-31')
    dates = pd.date_range('2007-12-31', '2009-12-31')
    # symbols = ['ML4T-220']
    symbols = ['IBM']
    N = 20
    predY_train, trainY, y_df_current, learner_data = LinReg_stock_learner.run_stock_learner(dates, symbols, N)
    learner_data = learner_data[:-5]

    predY_train_df = pd.DataFrame(predY_train, columns=['Predicted y'])
    predY_train_df = predY_train_df.set_index(pd.DatetimeIndex(learner_data.index.values))

    trainY_df = pd.DataFrame(trainY, columns=['Train y'])
    trainY_df = trainY_df.set_index(pd.DatetimeIndex(learner_data.index.values))

    y_df = pd.DataFrame(trainY, columns=['actual_y'])
    y_df = y_df.set_index(pd.DatetimeIndex(learner_data.index.values))

    # plot predicted y, training y, and price
    ax = predY_train_df.plot(title="2009-2011 IBM Comparison of predicted y, training y, and price")
    y_df_current.plot(ax=ax)
    trainY_df.plot(ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()

    # determine whether to short or long
    short = []
    short_stop = []
    long = []
    long_stop = []

    i = 0
    while i < len(predY_train_df)-5:
        if predY_train_df.ix[i+5]['Predicted y'] >= predY_train_df.ix[i]['Predicted y']*1.01:
            long.append(predY_train_df.index[i]) # start short position
            long_stop.append(predY_train_df.index[i+5]) # stop short position
            i += 5 # skip 5 days ahead
        if predY_train_df.ix[i+5]['Predicted y'] <= predY_train_df.ix[i]['Predicted y']*(1 - 0.01):
            short.append(predY_train_df.index[i]) # start short position
            short_stop.append(predY_train_df.index[i+5]) # stop short position
            i += 5 # skip 5 days ahead
        i += 1

    # Create dataframes for dates for short and long
    a = np.zeros((len(short),3))
    symbol_short = symbols * len(short)
    order_short = ['SELL'] * len(short)
    shares_short = [100] * len(short)
    short_data = {'Symbol': symbol_short, 'Order': order_short, 'Shares': shares_short}
    short_df = pd.DataFrame(short_data, columns=['Symbol','Order','Shares'])
    short_df = short_df.set_index(pd.DatetimeIndex(short))

    a = np.zeros((len(short_stop),3))
    symbol_short_stop = symbols * len(short_stop)
    order_short_stop = ['BUY'] * len(short_stop)
    shares_short_stop = [100] * len(short_stop)
    short_stop_data = {'Symbol': symbol_short_stop, 'Order': order_short_stop, 'Shares': shares_short_stop}
    short_stop_df = pd.DataFrame(short_stop_data, columns=['Symbol','Order','Shares'])
    short_stop_df = short_stop_df.set_index(pd.DatetimeIndex(short_stop))

    a = np.zeros((len(long),3))
    symbol_long = symbols * len(long)
    order_long = ['BUY'] * len(long)
    shares_long = [100] * len(long)
    long_data = {'Symbol': symbol_long, 'Order': order_long, 'Shares': shares_long}
    long_df = pd.DataFrame(long_data, columns=['Symbol','Order','Shares'])
    long_df = long_df.set_index(pd.DatetimeIndex(long))

    a = np.zeros((len(long_stop),3))
    symbol_long_stop = symbols * len(long_stop)
    order_long_stop = ['SELL'] * len(long_stop)
    shares_long_stop = [100] * len(long_stop)
    long_stop_data = {'Symbol': symbol_long_stop, 'Order': order_long_stop, 'Shares': shares_long_stop}
    long_stop_df = pd.DataFrame(long_stop_data, columns=['Symbol','Order','Shares'])
    long_stop_df = long_stop_df.set_index(pd.DatetimeIndex(long_stop))

    results_df = pd.concat([short_df, short_stop_df, long_df, long_stop_df])
    results_df = results_df.sort_index()
    results_df.index.name = 'Date'
    results_df.to_csv("results_df.csv")
    marketsim.test_code()
    #
    #
    #
    # # Plot stops and entries
    # df = bollinger_strategy.get_data(symbols, dates)
    # ax = df[symbols].plot(title="2009-2011 IBM  Linear Regression Strategy", label='IBM')
    # predY_train_df.plot(ax=ax)
    # ax.set_ylim(ymin=100)
    # ax.set_ylim(ymax=200)
    # # Add lines
    # ax.vlines(long_stop_df.index, color='black', ymin=0, ymax=400)
    # ax.vlines(long_df.index, color='green', ymin=0, ymax=400)
    # ax.vlines(short_stop_df.index, color='black', ymin=0, ymax=400)
    # ax.vlines(short_df.index, color='red', ymin=0, ymax=400)
    #
    # # Add axis labels and legend
    # ax.set_xlabel("Date")
    # ax.set_ylabel("Price")
    # ax.legend(loc='upper left')
    # plt.show()
    #


if __name__ == "__main__":
    test_run()
