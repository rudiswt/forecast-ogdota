from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# import seaborn as sns
from datetime import datetime
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from random import random


df = pd.read_csv(filepath_or_buffer='matches.csv',usecols=['match_id','start_time','league_name','opposing_team_name','radiant_win', 'radiant','duration'], engine='python')
df['start_time'] = pd.to_datetime(df['start_time'],unit='s')
df = df[['match_id','start_time','league_name','opposing_team_name','radiant_win', 'radiant','duration']]
df = df.sort_values(by=['opposing_team_name','start_time'])

def str_to_bool(s):
    if s == True:
         return False
    elif s == False:
         return True
    else:
         raise ValueError

def changeValueWin(kondisi,index):
    if kondisi == False:
        df.at[index,'radiant'] = True
        valuekudune = str_to_bool(df.at[index,'radiant_win'])
        df.at[index,'radiant_win'] = valuekudune

def hitungWinrate(value,periode):
    wr = value/periode
    # print(value,"/",periode,"=",wr)
    return round(wr,2)

def cariSeason(dataset):
    arrSeason = []
    for z in range(len(dataset)):
        season = dataset[z]/np.mean(dataset)
        arrSeason.append(round(season,2))
    return arrSeason


for a in range(len(df.index)-1, -1, -1):
    changeValueWin(df['radiant'][a], a)

# for b in range(len(df.index)-1, -1, -1):
newdf = df.loc[df['opposing_team_name'].str.contains("pire")== True]
newdf['Periode'] = np.arange(len(newdf))
newdf = newdf.set_index('Periode')
newdf.index = newdf.index+1
newdf['duration'] = newdf['duration'].div(60).round()

saledata = newdf['duration']
fit1 = Holt(saledata).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
fcast1 = fit1.forecast(12).rename("Holt's linear trend")

# fit1.forecast(12).plot(style='--', marker='o', color='red', legend=True)
# fit2.forecast(12).plot(style='--', marker='o', color='green', legend=True)

# print(fit1.fittedvalues,'-',fcast1)
# plt.show()

newdf['Forecast Duration'] = fit1.fittedvalues
newdf["Error Duration"] = newdf["duration"] - newdf["Forecast Duration"]
# abse = (abs(newdf["Error Duration"]))
# sqe = round(abse * abse,2)
# newdf['ABS Error Dur'] = abse
# newdf['Squared Error Dur'] = sqe
# pse = newdf['ABS Error Dur'] / newdf["duration"]
# newdf['Percent Error Dur'] = round(pse,4)

x=0
for c in range(len(newdf.index)):
    x += int(newdf.iloc[c]['radiant_win'] == True)
    c += 1
    winrate = hitungWinrate(x,c)

    newdf.loc[newdf.index[c-1],'Winrate'] = winrate*100

# # Forcast kedua, nilainya sama dengan nilai permintaan pertama
# arrWin = [np.nan]
# arrWin.append(newdf.Winrate.to_numpy()[0])
# for t in range(1,len(newdf.Winrate.to_numpy())-1):
#     arrWin.append(round((1-alpha)*arrWin[-1]+alpha*newdf.Winrate.to_numpy()[t],2))

saledata = newdf['Winrate']
fit2 = Holt(saledata).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
fcast2 = fit2.forecast(12).rename("Holt's linear trend")
newdf['duration'].plot(style='--', color='red', legend=True)
fit2.fittedvalues.plot(style='--', color='green', legend=True)

newdf['Forecast Winrate'] = fit2.fittedvalues
newdf["Error Winrate"] = newdf["Winrate"] - newdf["Forecast Winrate"]
# absew = (abs(newdf["Error Winrate"]))
# sqew = round(absew * absew,2)
# newdf['ABS Error Wr'] = absew
# newdf['Squared Error Wr'] = sqew
# psew = newdf['ABS Error Wr'] / newdf["Winrate"]
# newdf['Percent Error Wr'] = round(psew,4)

newdf = newdf.drop(columns=['radiant','match_id'])
newdf = newdf.rename({'radiant_win': 'Win', 'opposing_team_name':'Opposing Team', 'start_time':'Start Time','league_name':'League Name'}, axis='columns')
print(newdf)

# bias = np.mean(newdf["Error Winrate"])
# mad = (abs(newdf["Error Winrate"]).sum())/(len(newdf.index)-1)
# mse = np.mean(sqew)
# mape = abs(psew).sum()/(len(newdf.Winrate.to_numpy())-1)

# print("")
# print("BIAS:",(bias).round(2))
# print("MAD:",(mad).round(2))
# print("MSE:", (mse).round(2))
# print("MAPE:", (mape).round(2))
# # newdf.to_csv(r'match.csv')


newdf[["Winrate","Forecast Winrate"]].plot(title="Graph Winrate")
newdf[["duration","Forecast Duration"]].plot(title="Graph Duration")
plt.show()