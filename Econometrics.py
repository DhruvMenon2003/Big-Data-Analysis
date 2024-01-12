# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 17:48:05 2023

@author: lenovo
"""

"""Cleanup the Data"""

import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
df = pd.read_excel(r"C:\Users\lenovo\Downloads\stuntung_sanitation.xlsx")
null_values = df.isnull().sum()
print("Total NaN values:", null_values.sum())

"""Data Exploration"""
#Data epxloration
df_count = df['d1'].value_counts().reset_index()
df_count.columns = ['source', 'count']

df_count['percentage'] = df_count['count'] / df_count['count'].sum() * 100

labels = {
    11: "Piped into dwelling",
    12: "Piped into compound, yard or plot",
    13: "Piped to neighbor",
    14: "Public tap / standpipe",
    15: "Borehole or tubewell",
    21: "Protected well",
    22: "Unprotected well",
    31: "Protected spring",
    32: "Unprotected spring",
    33: "Rain water",
    41: "Water truck",
    42: "Water cart",
    5: "Water Kiosk",
    61: "Bottled Water",
    62: "Sachet water",
    71: "River", 
    72: "Stream", 
    73: "Dam", 
    74: "Lake", 
    75: "Pond", 
    76: "Canal", 
    77: "Irrigation Channel"
}

df_count['labels'] = df_count['source'].map(labels)

# Create the pie chart
plt.pie(df_count['count'], labels=df_count['labels'], autopct="%1.1f%%", startangle=140)

# Equal aspect ratio ensures that pie is drawn as a circle.
plt.axis("equal")  

# Set the title
plt.title("Proportions of the Main Sources of Drinking Water")

# Create legend for all sources with their corresponding percentages
legend_labels = [f"{label} ({perc}%)"
                 for label, perc in zip(df_count['labels'], df_count['percentage'].round(1))]

plt.legend(legend_labels, bbox_to_anchor=(1, 1), loc="upper left")

# Show the pie chart
plt.show()



# Make a bar chart showing the distribution of toilet facility type. 
plt.figure(figsize=(20, 10))
counts = df["d6"].value_counts()
ax = counts.plot(kind="bar")
plt.xticks(rotation=0)
plt.title("Distribution of Toilet Facility Type")
plt.xlabel("Toilet Facility Type")
plt.ylabel("Count")

# Calculate percentages and set them as bar labels
total = counts.sum()
percentages = ['{:.1f}%'.format(value * 100 / total) for value in counts]
ax.bar_label(ax.containers[0], labels=percentages, label_type='edge')

plt.tight_layout()
plt.show()
"""Hypothesis Testing"""
# Perform Chi-square test
contingency_table = pd.crosstab(df['stunting'], df['fidg'])
chi2, p, dof, expected = stats.chi2_contingency(contingency_table)

print(f'Chi-square Statistic: {chi2}, p-value: {p}')
if p < 0.05:
    print("We reject the null hypothesis and conclude that there is an association between stunting and income.")
else:
    print("We fail to reject the null hypothesis and conclude that there is no sufficient evidence of an association between stunting and income.")

# Bar plot with SEM
means = df.groupby('fidg')['stunting'].mean()
errors = df.groupby('fidg')['stunting'].sem()

fig, ax = plt.subplots()

means.plot.bar(yerr=errors, ax=ax, capsize=4)
ax.set_title('Stunting vs Income with SEM error bars')
ax.set_ylabel('Proportion Stunted')
ax.set_xlabel('Income Level')
plt.xticks(rotation=0)
plt.show()

# Define the dependent variable and the independent variable
X = df['e4']  # independent variable
y = df['stunting']  # dependent variable

# Add constant to the independent variable
X = sm.add_constant(X)

# Fit the logistic regression model
model = sm.Logit(y, X)
result = model.fit()

print(result.summary())
p_value = result.pvalues[1]

print(f'\np-value for dietary_diversity: {p_value}')

if p_value < 0.05:
    print("We reject the null hypothesis and conclude that there is an association between stunting and dietary diversity.")
else:
    print("We fail to reject the null hypothesis and conclude that there is no sufficient evidence of an association between stunting and dietary diversity.")

# Bar plot with SEM
means = df.groupby('e4')['stunting'].mean()
errors = df.groupby('e4')['stunting'].sem()

fig, ax = plt.subplots()

means.plot.bar(yerr=errors, ax=ax, capsize=4)
ax.set_title('Stunting vs Dietary Diversity with SEM error bars')
ax.set_ylabel('Proportion Stunted')
ax.set_xlabel('Dietary Diversity')
plt.xticks(rotation=0)
plt.show()

contingency_table = pd.crosstab(df['stunting'], df['d6'])
chi2, p, dof, expected = stats.chi2_contingency(contingency_table)

print(f'Chi-square Statistic: {chi2}, p-value: {p}')

if p < 0.05:
    print("We reject the null hypothesis and conclude that there is an association between stunting and toilet type.")
else:
    print("We fail to reject the null hypothesis and conclude that there is no sufficient evidence of an association between stunting and toilet type.")






