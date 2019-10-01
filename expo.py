from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# import seaborn as sns
from datetime import datetime


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

def calcSma(data, smaPeriod):
    j = next(i for i, x in enumerate(data) if x is not None)
    our_range = range(len(data))[j + smaPeriod - 1:]
    empty_list = [None] * (j + smaPeriod - 1)
    sub_result = [np.mean(data[i - smaPeriod + 1: i + 1]) for i in our_range]

    return np.array(empty_list + sub_result)

for a in range(len(df.index)-1, -1, -1):
    changeValueWin(df['radiant'][a], a)

# for b in range(len(df.index)-1, -1, -1):
newdf = df.loc[df['opposing_team_name'].str.contains("pire")== True]
newdf['Periode'] = np.arange(len(newdf))
newdf = newdf.set_index('Periode')
newdf.index = newdf.index+1
newdf['duration'] = newdf['duration'].div(60).round()

# short_rolling = newdf['duration'].rolling(window=4).mean()
arrDur = [np.nan]
arrDur.append(newdf.duration.to_numpy()[0])
alpha = 0.3
for t in range(1,len(newdf.duration.to_numpy())-1):
    arrDur.append(round((1-alpha)*arrDur[-1]+alpha*newdf.duration.to_numpy()[t],2))

newdf['Forecast Duration'] = arrDur
newdf["Error Duration"] = newdf["duration"] - newdf["Forecast Duration"]
abse = (abs(newdf["Error Duration"]))
sqe = round(abse * abse,2)
newdf['ABS Error Dur'] = abse
newdf['Squared Error Dur'] = sqe
pse = newdf['ABS Error Dur'] / newdf["duration"]
newdf['Percent Error Dur'] = round(pse,4)

x=0
for c in range(len(newdf.index)):
    x += int(newdf.iloc[c]['radiant_win'] == True)
    c += 1
    winrate = hitungWinrate(x,c)

    newdf.loc[newdf.index[c-1],'Winrate'] = winrate*100

# Forcast kedua, nilainya sama dengan nilai permintaan pertama
arrWin = [np.nan]
arrWin.append(newdf.Winrate.to_numpy()[0])
for t in range(1,len(newdf.Winrate.to_numpy())-1):
    arrWin.append(round((1-alpha)*arrWin[-1]+alpha*newdf.Winrate.to_numpy()[t],2))

newdf['Forecast Winrate'] = arrWin
newdf["Error Winrate"] = newdf["Winrate"] - newdf["Forecast Winrate"]
absew = (abs(newdf["Error Winrate"]))
sqew = round(absew * absew,2)
newdf['ABS Error Wr'] = absew
newdf['Squared Error Wr'] = sqew
psew = newdf['ABS Error Wr'] / newdf["Winrate"]
newdf['Percent Error Wr'] = round(psew,4)

newdf = newdf.drop(columns=['radiant','match_id'])
newdf = newdf.rename({'radiant_win': 'Win', 'opposing_team_name':'Opposing Team', 'start_time':'Start Time','league_name':'League Name'}, axis='columns')
print(newdf)

bias = np.mean(newdf["Error Winrate"])
mad = (abs(newdf["Error Winrate"]).sum())/(len(newdf.index)-1)
mse = np.mean(sqew)
mape = abs(psew).sum()/(len(newdf.Winrate.to_numpy())-1)

print("")
print("BIAS:",(bias).round(2))
print("MAD:",(mad).round(2))
print("MSE:", (mse).round(2))
print("MAPE:", (mape).round(2))
# newdf.to_csv(r'match.csv')


newdf[["Winrate","Forecast Winrate"]].plot(title="Graph Winrate")
newdf[["duration","Forecast Duration"]].plot(title="Graph Duration")
# plt.show()