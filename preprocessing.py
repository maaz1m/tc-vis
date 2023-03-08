# preprocessing.py

import requests
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# pulling data from JSON endpoint
data = requests.get('https://www.levels.fyi/js/salaryData.json').json()
comp_df = pd.DataFrame(data)

comp_df.head()

# dropping empty columns
comp_df = comp_df.drop(['cityid', 'dmaid','rowNumber', 'otherdetails'], axis=1)

# setting blanks as NAs
comp_df = comp_df.replace("", np.nan)
size = comp_df.shape[0]

pd.DataFrame([[var, comp_df[var].isnull().sum(), (comp_df[var].isnull().sum())/comp_df.shape[0]] for var in comp_df.columns], columns=['column_name', 'missing_total', 'missing_ratio'])

# changing datetime type
comp_df.timestamp = pd.to_datetime(comp_df.timestamp)

# changing othertypes
comp_df.totalyearlycompensation = comp_df.totalyearlycompensation.astype('float64')*1000
comp_df.basesalary = comp_df.basesalary.astype('float64')*1000
comp_df.stockgrantvalue = comp_df.stockgrantvalue.astype('float64')*1000
comp_df.bonus = comp_df.bonus.astype('float64')*1000
comp_df.yearsofexperience = comp_df.yearsofexperience.astype('int64')
comp_df.yearsatcompany = comp_df.yearsatcompany.astype('int64')

# adding date and year features
comp_df['date'] = comp_df['timestamp'].dt.date
comp_df['year'] = comp_df['timestamp'].dt.year

sns.boxplot(data=comp_df, x='totalyearlycompensation')
plt.show()

# removing outliers
not_outliers = comp_df['totalyearlycompensation'].between(comp_df['totalyearlycompensation'].quantile(.05),comp_df['totalyearlycompensation'].quantile(.95)) & comp_df['yearsofexperience'].between(comp_df['yearsofexperience'].quantile(.05),comp_df['yearsofexperience'].quantile(.95))
comp_df = comp_df[not_outliers]

# save as csv
comp_df.to_csv('tc_data.csv', index=False)