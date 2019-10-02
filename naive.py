import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

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
aust = newdf['duration']
newdf['Forecast duration'] = aust.shift(1)
# newdf = newdf.merge(newdf['Forecast duration'], how="outer", left_index=True, right_index=True)

newdf["Error Duration"] = newdf["duration"] - newdf["Forecast duration"]
abse = (abs(newdf["Error Duration"]))
sqe = abse * abse
newdf['ABS Error Dur'] = abse
newdf['Squared Error Dur'] = sqe

x=0
for c in range(len(newdf.index)):
    x += int(newdf.iloc[c]['radiant_win'] == True)
    c += 1
    winrate = hitungWinrate(x,c)
    newdf.loc[newdf.index[c-1],'Winrate'] = winrate*100

aust = newdf['Winrate']
newdf['Forecast Winrate'] = aust.shift(1)
newdf["Error Winrate"] = newdf["Winrate"] - newdf["Forecast Winrate"]
absew = (abs(newdf["Error Winrate"]))
sqew = absew * absew
newdf['ABS Error Wr'] = absew
newdf['Squared Error Wr'] = sqew

newdf = newdf.drop(columns=['radiant','match_id'])
newdf = newdf.rename({'radiant_win': 'Win', 'opposing_team_name':'Opposing Team', 'start_time':'Start Time','league_name':'League Name'}, axis='columns')

bias = np.mean(newdf["Error Winrate"])
mad = (abs(newdf["Error Winrate"]).sum())/(len(newdf.index)-1)
mse = np.mean(sqew)

print("")
print("BIAS:",(bias).round(2))
print("MAD:",(mad).round(2))
print("MSE:", (mse).round(2))
# newdf.to_csv(r'fixmatch.csv')


newdf[["Winrate","Forecast Winrate"]].plot(title="Graph Winrate")
newdf[["duration","Forecast duration"]].plot(title="Graph Duration")
print(newdf)
plt.show()