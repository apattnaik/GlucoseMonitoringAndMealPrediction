import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import itertools
from statsmodels.tsa.seasonal import seasonal_decompose

df = pd.read_csv('data/cgm_to_meal.csv')
Y = df['cgm']
X = range(len(Y))
df['cgm'] = df['cgm'].fillna(0)
print(df.head())
decomposition = seasonal_decompose(df.cgm,freq=1)
# fig = plt.figure(figsize=(15,8))
# fig = decomposition.plot()
# plt.show()

from statsmodels.tsa.stattools import adfuller


def test_stationarity(timeseries):
    # Determing rolling statistics
    rolmean = timeseries.rolling(1).mean()
    rolstd = timeseries.rolling(1).mean()

    # Plot rolling statistics:
    fig = plt.figure(figsize=(12, 8))
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show()

    # Perform Dickey-Fuller test:
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print (dfoutput)

# test_stationarity(df.cgm)
df.cgm_log= df.cgm.apply(lambda x: np.log(x))
test_stationarity(df.cgm_log)