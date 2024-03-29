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

fit1 = ExponentialSmoothing(aust, seasonal_periods=4, trend='add', seasonal='add').fit(use_boxcox=True)
fit2 = ExponentialSmoothing(aust, seasonal_periods=4, trend='add', seasonal='mul').fit(use_boxcox=True)
fit3 = ExponentialSmoothing(aust, seasonal_periods=4, trend='add', seasonal='add', damped=True).fit(use_boxcox=True)
fit4 = ExponentialSmoothing(aust, seasonal_periods=4, trend='add', seasonal='mul', damped=True).fit(use_boxcox=True)
results=pd.DataFrame(index=[r"$\alpha$",r"$\beta$",r"$\phi$",r"$\gamma$",r"$l_0$","$b_0$","SSE"])
params = ['smoothing_level', 'smoothing_slope', 'damping_slope', 'smoothing_seasonal', 'initial_level', 'initial_slope']
results["Additive"]       = [fit1.params[p] for p in params] + [fit1.sse]
results["Multiplicative"] = [fit2.params[p] for p in params] + [fit2.sse]
results["Additive Dam"]   = [fit3.params[p] for p in params] + [fit3.sse]
results["Multiplica Dam"] = [fit4.params[p] for p in params] + [fit4.sse]

ax = aust.plot(figsize=(10,6), marker='o', color='black', title="Forecasts from Holt-Winters' multiplicative method" )
ax.set_ylabel("Winrate")
ax.set_xlabel("Periode")
aust.rename('Duration').plot(ax=ax, style='--', color='red', legend=True)
fit2.fittedvalues.rename('Holt-Winters < Total Periode').plot(ax=ax, style='--', color='green', legend=True)
fit2.forecast(4).rename('Holt-Winters > Total Periode').plot(ax=ax, style='--', marker='o', color='green', legend=True)

# fit1.forecast(8).rename('Holt-Winters (add-add-seasonal)').plot(ax=ax, style='--', marker='o', color='red', legend=True)

dfs = pd.DataFrame(np.c_[aust, fit2.level, fit2.slope, fit2.season, fit2.fittedvalues],
                  columns=[r'Duration',r'Level Dur',r'Trend Dur',r'Seasonal Dur',r'Forecast Duration'],index=aust.index)
hh = dfs.append(fit2.forecast(4).rename(r'Forecast Duration').to_frame(), sort=True)

x=0
for c in range(len(newdf.index)):
    x += int(newdf.iloc[c]['radiant_win'] == True)
    c += 1
    winrate = hitungWinrate(x,c)
    newdf.loc[newdf.index[c-1],'Winrate'] = winrate*100

austt = newdf['Winrate']
fit5 = ExponentialSmoothing(austt, seasonal_periods=4, trend='add', seasonal='add').fit(use_boxcox=True)
fit6 = ExponentialSmoothing(austt, seasonal_periods=4, trend='add', seasonal='mul').fit(use_boxcox=True)
fit7 = ExponentialSmoothing(austt, seasonal_periods=4, trend='add', seasonal='add', damped=True).fit(use_boxcox=True)
fit8 = ExponentialSmoothing(austt, seasonal_periods=4, trend='add', seasonal='mul', damped=True).fit(use_boxcox=True)
results=pd.DataFrame(index=[r"$\alpha$",r"$\beta$",r"$\phi$",r"$\gamma$",r"$l_0$","$b_0$","SSE"])
params = ['smoothing_level', 'smoothing_slope', 'damping_slope', 'smoothing_seasonal', 'initial_level', 'initial_slope']
results["Additive"]       = [fit5.params[p] for p in params] + [fit1.sse]
results["Multiplicative"] = [fit6.params[p] for p in params] + [fit2.sse]
results["Additive Dam"]   = [fit7.params[p] for p in params] + [fit3.sse]
results["Multiplica Dam"] = [fit8.params[p] for p in params] + [fit4.sse]

ax = austt.plot(figsize=(10,6), marker='o', color='black', title="Forecasts from Holt-Winters' multiplicative method" )
ax.set_ylabel("Winrate")
ax.set_xlabel("Periode")
aust.rename('Winrate').plot(ax=ax, style='--', color='red', legend=True)
fit6.fittedvalues.rename('Holt-Winters < Total Periode').plot(ax=ax, style='--', color='green', legend=True)
fit6.forecast(4).rename('Holt-Winters > Total Periode').plot(ax=ax, style='--', marker='o', color='green', legend=True)

hh['Winrate'] = austt
hh['Level Wr'] = fit6.level
hh['Trend Wr'] = fit6.slope
hh['Seasonal Wr']= fit6.season
hh['Forecast Wr'] = fit6.fittedvalues
hh = hh.append(fit6.forecast(4).rename(r'Forecast Wr').to_frame(), sort=True)
# print(aust)
print('-------------------------------------------------')

print(results)
print('-------------------------------------------------')

print(hh)
print('-------------------------------------------------')
plt.show()