# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 07:45:23 2021

@author: HP
"""
import pandas as pd
import os
import matplotlib.pyplot as plt
import dateutil
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))

df = pd.read_excel(dir_path+"//cryptoslam_sales//cryptoslam_cryptopunks.xlsx")
df.drop("Unnamed: 0",axis=1,inplace=True)
df['month'] = df['Sold'].dt.month
df['year'] = df['Sold'].dt.year
df['year_month'] = pd.to_datetime(df[['year', 'month']].assign(Day=1))

df["USD"] = df["USD"].apply(lambda x:x[1:])
df["USD"] = df["USD"].apply(lambda x: x.replace(',', ''))
df["USD"] = df["USD"].apply(lambda x: float(x))

# df['month_year'] = df['Sold'].dt.to_period('M')

# df.hist(column=["USD"])
x = df["USD"]
# plt.scatter(df["month_year"], df["USD"])
plt.plot(df["USD"], linestyle = 'dashed')


month_and_usd = df[["year_month","USD"]]
# december =  dateutil.parser.parse("2020-12-12").to_period('M')
month_and_usd.set_index("year_month",inplace=True)
year_2021=month_and_usd[month_and_usd.index > dateutil.parser.parse("2020-12-12")]

grouped_by_month_mean = year_2021.groupby(year_2021.index).mean()
plt.bar(grouped_by_month_mean.index, grouped_by_month_mean["USD"])
grouped_by_month=grouped_by_month_mean.reset_index()
grouped_by_month.plot.bar(x="year_month", y="USD" )


## Flour price vs Average price
grouped_by_month_mean = year_2021.groupby(year_2021.index).mean().reset_index()
grouped_by_month_min = year_2021.groupby(year_2021.index).min().reset_index()

fig,ax = plt.subplots()
ax.plot(grouped_by_month_mean.index, grouped_by_month_mean["USD"], label="Average Price") # problem with datetime column "year_month"
ax.plot(grouped_by_month_min.index, grouped_by_month_min["USD"], label="Minimum Price")
plt.legend()
plt.show()
plt.close(fig)

## item amount vs sales volume 






