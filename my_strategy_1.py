__author__ = 'Raymond Yeh'


import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import marketsim

def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))


def get_data(symbols, dates):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df = df.join(df_temp)
        df = df.dropna(subset=["IBM"])
    return df


def plot_data(df, title="Stock prices"):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()


def get_rolling_mean(values, window):
    """Return rolling mean of given values, using specified window size."""
    return pd.rolling_mean(values, window=window)


def get_rolling_std(values, window):
    """Return rolling standard deviation of given values, using specified window size."""
    # Compute and return rolling standard deviation
    return pd.rolling_std(values, window=window)


def get_bollinger_bands(rm, rstd):
    """Return upper and lower Bollinger Bands."""
    # Compute upper_band and lower_band
    upper_band = rm + rstd*2
    lower_band = rm - rstd*2
    return upper_band, lower_band


def test_run():
    # Read data
    dates = pd.date_range('2007-12-31', '2009-12-31')
    symbols = ['IBM']
    df = get_data(symbols, dates)

    # Compute Bollinger Bands
    # 1. Compute rolling mean
    rolling_mean_short = get_rolling_mean(df['IBM'], window=10)

    df_shift = df.shift(periods=1)
    rolling_mean_short_shift = rolling_mean_short.shift(periods=1)

    frames = [df, df_shift, rolling_mean_short, rolling_mean_short_shift]
    result = pd.concat(frames, axis=1)
    result = result.ix[20:]
    result.columns = ['df', 'df_shift', 'rolling_mean_short', 'rolling_mean_short_shift']

    short = []
    short_stop = []
    long = []
    long_stop = []

    short_flag = 0
    short_stop_flag = 0
    long_flag = 0
    long_stop_flag = 0

    for result_index, result_row in result.iterrows():
        if result_row['df_shift'] >= result_row['rolling_mean_short_shift'] and result_row['df'] < result_row['rolling_mean_short'] and long_flag == 0:
            long.append(result_index)
            long_flag = 1
        if result_row['df_shift'] <= result_row['rolling_mean_short_shift'] and result_row['df'] > result_row['rolling_mean_short'] and short_flag == 0:
            if long_flag == 1:
                long_stop.append(result_index)
                long_flag = 0

    # Create dataframes for dates for short and long
    a = np.zeros((len(long),3))
    symbol_long = ['IBM'] * len(long)
    order_long = ['BUY'] * len(long)
    shares_long = [100] * len(long)
    long_data = {'Symbol': symbol_long, 'Order': order_long, 'Shares': shares_long}
    long_df = pd.DataFrame(long_data, columns=['Symbol','Order','Shares'])
    long_df = long_df.set_index(pd.DatetimeIndex(long))

    a = np.zeros((len(long_stop),3))
    symbol_long_stop = ['IBM'] * len(long_stop)
    order_long_stop = ['SELL'] * len(long_stop)
    shares_long_stop = [100] * len(long_stop)
    long_stop_data = {'Symbol': symbol_long_stop, 'Order': order_long_stop, 'Shares': shares_long_stop}
    long_stop_df = pd.DataFrame(long_stop_data, columns=['Symbol','Order','Shares'])
    long_stop_df = long_stop_df.set_index(pd.DatetimeIndex(long_stop))

    results_df = pd.concat([long_df, long_stop_df])
    results_df = results_df.sort_index()
    results_df.index.name = 'Date'
    results_df.to_csv("results_df.csv")
    # marketsim.test_code()



    # # Plot raw IBM values, rolling mean and Bollinger Bands
    ax = df['IBM'].plot(title="IBM Moving Average Strategy", label='IBM')
    rolling_mean_short.plot(label='Rolling mean', color='green', ax=ax)

    # Add lines
    ax.vlines(long_stop_df.index, color='red', ymin=0, ymax=200)
    ax.vlines(long_df.index, color='green', ymin=0, ymax=200)

    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')
    plt.show()




if __name__ == "__main__":
    test_run()
