# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 05:52:55 2023

@author: lenovo
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 17:48:05 2023

@author: lenovo
"""

"""Cleanup the Data"""

import pandas as pd
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

df = pd.read_csv(r"C:\Users\lenovo\Downloads\Savola_et_al_2020_DR_with_injury_and_infection_stressors_CSV_Data.csv")
null_values = df.isnull().sum()

total_missing_values = null_values.sum() 
print("Total null/NA values:", total_missing_values)

all_columns_have_missing = True
max_count = 0
max_column = ""

for column in df.columns:
    null_count = df[column].isnull().sum()
    print(column, null_count)

    if null_count == 0:
        all_columns_have_missing = False

    if null_count > max_count:
        max_count = null_count
        max_column = column

if all_columns_have_missing:
    print("All columns have missing values.")
else:
    print("Not all columns have missing values.")

print("Column with the maximum number of missing elements:", max_column)
# """Data Exploration""
#How many flies in the control group survived until day 20?
survived_control_flies_day20 = df[(df["Treat"] == "Control") & (df["Dead"] == 0) & (df["Date"] == 20)]

# Total number of control flies that were marked (both survived and dead, not escaped) on Day20? 
total_marked_control_flies = df[(df["Treat"] == "Control") & (df["Date"] == 20) & (~df["Dead"].isna())]
# Group by diet and count the number of vials for survived flies
survived_flies_per_diet = survived_control_flies_day20.groupby('Protein')['Vial'].count()

# Group by diet and count the number of vials for total marked flies (excluding escapes)
total_marked_flies_per_diet = total_marked_control_flies.groupby('Protein')['Vial'].count()

# Calculate the fraction of flies alive for each diet
fraction_alive_per_diet = (survived_flies_per_diet / total_marked_flies_per_diet) * 100

# Create a bar chart
fraction_alive_per_diet.plot(kind='bar', figsize=(8, 6))

plt.title("Fraction of Control Flies Alive on Day 20 for Each Diet")
plt.xlabel("Diet")
plt.ylabel("Fraction of Flies Alive (%)")
plt.ylim([0, 100])  # Set the limits of the y-axis to show percentages from 0 to 100
plt.xticks(rotation=0)  # Rotate x-axis labels if necessary
plt.show()
# # """Hypothesis Testing"""
"""Null Hypothesis (H0): The average lifespan of unharmed (control) flies is the same across all different protein content diets.
Alternative Hypothesis (H1): The average lifespan of unharmed (control) flies differs between at least two different protein content diets.
"""
#ANOVA Test
control_flies_dead = df[(df["Treat"] == "Control") & (df["Dead"] == 1) & df["Date"].notna()]

# Calculate the average lifespan for each protein content percentage within the control flies
average_lifespan_per_group = control_flies_dead.groupby('Protein')['Date'].mean().reset_index()

print(average_lifespan_per_group)

plt.figure(figsize=(10, 6))
control_flies_dead.boxplot(column='Date', by='Protein', grid=False)
plt.title('Lifespan vs Protein Content in Food')
plt.xlabel('Protein Content (%)')
plt.ylabel('Average Lifespan (Experimental Day)')
plt.show()

lifespan_groups = [group['Date'].values for name, group in control_flies_dead.groupby('Protein')]

# Perform ANOVA
anova_result = scipy.stats.f_oneway(*lifespan_groups)
print(f"ANOVA result: F-statistic = {anova_result.statistic}, p-value = {anova_result.pvalue}")

# Conclusion based on the p-value
alpha = 0.05  # significance level
if anova_result.pvalue < alpha:
    print("Reject the null hypothesis: There is a significant difference in average lifespan across the different protein content diets.")
else:
    print("Fail to reject the null hypothesis: There is no significant difference in average lifespan across the different protein content diets.")
#We're going to repeat the same set of steps again..
"""
Hypothesis
Null Hypothesis (H0): There is no difference in the average lifespan of control and injured flies on a low protein (<30%) diet.
Alternative Hypothesis (H1): There is a difference in the average lifespan of control and injured flies on a low protein (<30%) diet.
"""
# Filter for low protein (<30%) for control and injured flies..
low_protein_flies = df[(df["Protein"] < 30) & ((df["Treat"] == "Control") | (df["Treat"] == "Sham")) & (df["Dead"] == 1) & df["Date"].notna()]

# Create boxplot
plt.figure(figsize=(10, 6))
low_protein_flies.boxplot(column='Date', by='Treat', grid=False)
plt.title('Lifespan of Control vs Injured Flies on Low Protein Diet')
plt.xlabel('Treatment')
plt.ylabel('Lifespan (Experimental Day)')
plt.show()

# Statistical Test
control_lifespans = low_protein_flies[low_protein_flies["Treat"] == "Control"]['Date']
injured_lifespans = low_protein_flies[low_protein_flies["Treat"] == "Sham"]['Date']
ttest_result = scipy.stats.ttest_ind(control_lifespans, injured_lifespans)

print(f"T-test result: statistic = {ttest_result.statistic}, p-value = {ttest_result.pvalue}")

# Conclusion based on the p-value
alpha = 0.05  # significance level
if ttest_result.pvalue < alpha:
    print("Reject the null hypothesis: There is a a significant difference in the average lifespan of control and injured flies on a low protein (<30%) diet")
else:
    print("Fail to reject the null hypothesis: There is no difference in the average lifespan of control and injured flies on a low protein (<30%) diet.")
"""
Hypothesis
Null Hypothesis (H0): There is no difference in the average lifespan of injured and infected flies on a low protein (<30%) diet.
Alternative Hypothesis (H1): There is a difference in the average lifespan of injured and infected flies on a low protein (<30%) diet.
"""
# Filter for low protein (<30%) for control and injured flies..
low_protein_flies = df[(df["Protein"] < 30) & ((df["Treat"] == "Sham") | (df["Treat"] == "Infection")) & (df["Dead"] == 1) & df["Date"].notna()]

# Create boxplot
plt.figure(figsize=(10, 6))
low_protein_flies.boxplot(column='Date', by='Treat', grid=False)
plt.title('Lifespan of Injured vs Infected Flies on Low Protein Diet')
plt.xlabel('Treatment')
plt.ylabel('Lifespan (Experimental Day)')
plt.show()

# Statistical Test
infected_lifespans = low_protein_flies[low_protein_flies["Treat"] == "Infection"]['Date']
injured_lifespans = low_protein_flies[low_protein_flies["Treat"] == "Sham"]['Date']
ttest_result = scipy.stats.ttest_ind(infected_lifespans, injured_lifespans)

print(f"T-test result: statistic = {ttest_result.statistic}, p-value = {ttest_result.pvalue}")

# Conclusion based on the p-value
alpha = 0.05  # significance level
if ttest_result.pvalue < alpha:
    print("Reject the null hypothesis: There is a a significant difference in the average lifespan of infected and injuregd flies(much lower average lifespan) on a low protein (<30%) diet")
else:
    print("Fail to reject the null hypothesis: There is no difference in the average lifespan of infected and injured flies on a low protein (<30%) diet.")

"""
Hypothesis
Null Hypothesis (H0): The severity of the treatment (control, injury, infection) has no effect on the fecundity of the subjects on a low protein (<30%) diet.
Alternative Hypothesis (H1): The severity of the treatment affects the fecundity of the subjects on a low protein (<30%) diet, with fecundity decreasing as the severity of treatment increases.
"""
# Map the 'Treat' column to an ordinal variable.
df['Treatment_Ordinal'] = df['Treat'].map({'Control': 0, 'Sham': 1, 'Infection': 2})

# Filter for low protein (<30%) and consider only the data within 50 days.
low_protein_data = df[(df["Protein"] < 30) & (df["Date"] <= 50)]
low_protein_data = low_protein_data.dropna()
control_eggs_distribution = low_protein_data[low_protein_data['Treatment_Ordinal'] == 0]['Eggs'].value_counts().sort_index()
injury_eggs_distribution = low_protein_data[low_protein_data['Treatment_Ordinal'] == 1]['Eggs'].value_counts().sort_index()
infection_eggs_distribution = low_protein_data[low_protein_data['Treatment_Ordinal'] == 2]['Eggs'].value_counts().sort_index()

print("Control Group Egg Distribution:\n", control_eggs_distribution)
print("\nInjury Group Egg Distribution:\n", injury_eggs_distribution)
print("\nInfection Group Egg Distribution:\n", infection_eggs_distribution)
plt.figure(figsize=(10, 6))
boxplot = low_protein_data.boxplot(column='Eggs', by='Treatment_Ordinal', grid=False)
plt.title('Boxplot of Egg Counts by Treatment Category')
plt.xlabel('Treatment Severity (0=Control, 1=Sham, 2=Infection)')
plt.ylabel('Egg Count')
plt.xticks([1, 2, 3], ['Control', 'Injury', 'Infection'])

# Group the data by 'Treatment_Ordinal' and calculate the mean of 'Egg_Count' over the 50 days.
grouped_data = low_protein_data.groupby('Treatment_Ordinal')['Eggs'].mean().reset_index()

# Now 'grouped_data' contains the average 'Egg_Count' for each 'Treatment_Ordinal' category.

# Fit a linear regression model to the averaged data.
X = sm.add_constant(grouped_data['Treatment_Ordinal'])  # Adds a constant term to the predictor
Y = grouped_data['Eggs']

# Fit the OLS model.
model = sm.OLS(Y, X).fit()

# Plot the averaged data.
plt.scatter(grouped_data['Treatment_Ordinal'], Y, alpha=0.5, label='Averaged Data Points')

# Plot the regression fit.
plt.plot(grouped_data['Treatment_Ordinal'], model.fittedvalues, 'r-', label='OLS Regression Line')

# Add legend, labels, and title to the plot.
plt.legend()
plt.xlabel('Treatment Ordinal')
plt.ylabel('Egg Count')
plt.title('Regression Analysis of Treatment Effect on Egg Count')

# Show the plot.
plt.show()

# Output the summary of the regression model.
print(model.summary())

# Extract the p-value for the Treatment_Ordinal coefficient.
p_value = model.pvalues['Treatment_Ordinal']

# Print the p-value.
print(f"p-value for the Treatment_Ordinal coefficient: {p_value:.4f}")

# Determine if the result is significant.
alpha = 0.05
if p_value < alpha:
    print("Reject the null hypothesis: There is a significant effect of treatment severity on egg count.")
else:
    print("Fail to reject the null hypothesis: There is no significant effect of treatment severity on egg count.")
    
    