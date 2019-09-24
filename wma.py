from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import re
# import seaborn as sns
from datetime import datetime


df = pd.read_csv(filepath_or_buffer='matches.csv',usecols=['match_id','start_time','league_name','opposing_team_name','radiant_win', 'radiant','duration'])
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
    return round(wr,2)

for a in range(len(df.index)-1, -1, -1):
    changeValueWin(df['radiant'][a], a)

# for b in range(len(df.index)-1, -1, -1):
newdf = df.loc[df['opposing_team_name'].str.contains("pire")== True]
newdf['Periode'] = np.arange(len(newdf))
newdf = newdf.set_index('Periode')
newdf.index = newdf.index+1
newdf['duration'] = newdf['duration'].div(60).round()


arrayDuration = newdf.duration.to_numpy()
bobot = [0.1,0.3,0.6]
# print(arrayDuration)
arrForeDur = []
arrForeWin = []
periode = len(arrayDuration)

def filter3Bulan(pp,arr):
    rumus = 0
    if pp<2:
        rumus = np.nan
    else:
        kurang = pp - 3
        slicing = slice(kurang, pp)
        slicearr = arr[slicing]
        # print(slicearr)
        for k, p in enumerate(slicearr):
            u = bobot[k]*p      
            print(bobot[k],'x',p,'=',u)
            rumus += u
    return round(rumus,1)

for o in range(periode):
    arrForeDur.append(filter3Bulan(o,arrayDuration))

newdf['Forecast Duration'] = arrForeDur
newdf["Error Duration"] = newdf["duration"] - newdf["Forecast Duration"]
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

arrayWinrate = newdf.Winrate.to_numpy()

for p in range(periode):
    arrForeWin.append(filter3Bulan(p,arrayWinrate))


newdf['Forecast Winrate'] = arrForeWin
newdf["Error Winrate"] = newdf["Winrate"] - newdf["Forecast Winrate"]
absew = (abs(newdf["Error Winrate"]))
sqew = absew * absew
newdf['ABS Error Wr'] = absew
newdf['Squared Error Wr'] = sqew

newdf = newdf.drop(columns=['radiant','match_id'])
newdf = newdf.rename({'radiant_win': 'Win', 'opposing_team_name':'Opposing Team', 'start_time':'Start Time','league_name':'League Name'}, axis='columns')
print(newdf)

bias = np.mean(newdf["Error Winrate"])
mad = (abs(newdf["Error Winrate"]).sum())/(len(newdf.index)-1)
mse = np.mean(sqew)

print("")
print("BIAS:",(bias).round(2))
print("MAD:",(mad).round(2))
print("MSE:", (mse).round(2))
# newdf.to_csv(r'match.csv')


newdf[["Winrate","Forecast Winrate"]].plot(title="Graph Winrate")
newdf[["duration","Forecast Duration"]].plot(title="Graph Duration")
# plt.show()