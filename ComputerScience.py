# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 08:10:24 2023

@author: lenovo
"""

"""
What do the columns in the log represent?
 "A log message, as
illustrated in the following example, records a specific system
event with a set of fields: timestamp (the occurrence time
of the event, e.g., 2008-11-09 20:46:55,556), verbosity level
(the severity level of the event, e.g., INFO), and message
content that describes the event in free text."(Zhu et al.,2023)

1st field is time stamp.
Field 2 helps you identify which process generated the log message
Field 3 goes one step further telling you which thread of that process to help debug.
4th field is verbosity level(I,W,E,)
Last field is message content
"""
"""
Parsing the Data: We have 5 fields with a space separator so we can easily convert this into a Pandas Data Frame
"""
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Path to the log file
log_file = r"C:\Users\lenovo\Downloads\Android_v1\Android.log"

# Define the regular expression pattern
pattern = r"(\d{2}-\d{2}) +(\d{2}:\d{2}:\d{2}.\d{3}) +(\d+) +(\d+) +(\w) +(.*)"

# Read the log file and extract data using the pattern
data = []
with open(log_file,encoding="utf_8") as f:
    for line in f:
        match = re.match(pattern, line)
        if match:
            date,time, process_id, thread_id, verbosity, message = match.groups()
            data.append((date,time, process_id, thread_id, verbosity, message))

# Create the DataFrame from the extracted data
df = pd.DataFrame(data, columns=["date","time", "process_id", "thread_id", "verbosity", "message"])

# Print the DataFrame
print(df)
#Data Exoploration
# Data Exploration: Distribution of Events by Hour
# Extract hour from timestamp and create new column
df["hour"] = pd.to_datetime(df["time"]).dt.hour
hour_counts = df["hour"].value_counts().sort_index()

# Plot the histogram with sorted hours
plt.figure(figsize=(8, 6))
hour_counts.plot(kind="bar")

# Format x- and y-axis labels with units
plt.xlabel("Hour of Day (24-hour format)", fontsize=10)
plt.ylabel("Number of Events", fontsize=10)

# Set x-ticks to display all hours from 1 to 24
plt.xticks(range(1, 25))
plt.xticks(rotation=0, ha="right")
plt.title("Distribution of Events by Hour (Sorted)", fontsize=12)

plt.tight_layout()
plt.show()

# Data Exploration: Share of Programs in Log Messages
# Count occurrences of each program
program_counts = df["message"].str.split().str[0].value_counts()

total_count = program_counts.sum()
top_5_counts = program_counts.head(5).sum()
other_counts = total_count - top_5_counts

# Pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    [other_counts, *program_counts.head(5)],
    labels=["Other", *program_counts.head(5).index],
    autopct="%1.1f%%",
)
plt.title("Share of Programs in Log Messages", fontsize=12)

plt.tight_layout()
plt.show()

"""Hypothesis Testing"""
"""Based on the observation that the number of events is lower in the morning, peaks around night time (post 19:00), and declines during the early morning hours post-midnight, we can form the following hypothesis:

Null Hypothesis (H0): On an average, the number of events in the post-midnight time window is greater than the number of events in the post-afternoon time window.
Alternative Hypothesis (H1): On an average, less events occur in the post-midnight time window than in the post-afternoon time window.  """



# Convert Series to DataFrame
hour_counts_df = hour_counts.reset_index()
hour_counts_df.columns = ['Hour', 'EventCount']

# Filter for the time windows
midnight_events = hour_counts_df[(hour_counts_df['Hour'] >= 0) & (hour_counts_df['Hour'] < 8)]  
afternoon_events = hour_counts_df[(hour_counts_df['Hour'] >= 14) & (hour_counts_df['Hour'] <= 23)]

# Perform a hypothesis test two-sample t-test to compare the event counts
alpha = 0.05  # Significance level

# Assuming equal variances
_, p_value = stats.ttest_ind(midnight_events["EventCount"], afternoon_events["EventCount"], equal_var=True)

if p_value < alpha:
    conclusion = "Reject the null hypothesis. There is a significant difference in the number of events."
else:
    conclusion = "Fail to reject the null hypothesis. There is no significant difference in the number of events."

print(f"Midnight event count: {midnight_events['EventCount'].sum()}")
print(f"Afternoon event count: {afternoon_events['EventCount'].sum()}")
print(f"P-value: {p_value}")
print(conclusion)

# Create separate box plots for the midnight and afternoon events
# Visualize the distributions
plt.figure(figsize=(10, 6))

# Midnight events
plt.subplot(1, 2, 1)
sns.boxplot(y=midnight_events["EventCount"])
plt.title("Midnight Event Distribution")
plt.xlabel("Midnight")
plt.ylabel("EventCount")

# Afternoon events
plt.subplot(1, 2, 2)
sns.boxplot(y=afternoon_events["EventCount"])
plt.title("Afternoon Event Distribution")
plt.xlabel("Afternoon")
plt.ylabel("EventCount")

# Customize plot for clarity
plt.suptitle(f"Distribution of Events - Midnight vs. Afternoon (p={p_value:.3f})")
plt.tight_layout()
plt.show()#Conervt to data frame
program_counts_df = program_counts.reset_index()
program_counts_df.columns = ['Program', 'EventCount']

# Convert time to datetime for proper handling
df["time"] = pd.to_datetime(df["time"])

window_start = df["time"].min()
window_end = df["time"].max()
interval = pd.Timedelta(minutes=5) #5minute time interval

#Create a 5 minute time interval
df["time_window"] = pd.cut(df["time"], pd.date_range(start=window_start, end=window_end, freq=interval))

# Extract the program names from the 'message' column and count occurrences
df["Program"] = df["message"].str.split().str[0]

# Filter top 10 processes
top_10_processes = df['Program'].value_counts().head(10).index.tolist()

# Filter the dataframe for rows containing the top 10 processes
df_filtered = df[df['Program'].isin(top_10_processes)]

# Count the number of events for each process within each time interval
event_counts = (
    df_filtered.groupby(["time_window", "Program"])["Program"]
    .count()
    .to_frame(name="event_count")
    .reset_index()
)

# Pivot the data to have separate columns for each program and their counts
event_counts_pivot = event_counts.pivot(index="time_window", columns="Program", values="event_count").fillna(
    0
)

# Calculate the event rates for each program
for program in event_counts_pivot.columns:
    event_counts_pivot[f"{program}_rate"] = event_counts_pivot[program] / (5 * 60)

# Extract rates for each process
process_rates = event_counts_pivot[["SendBroadcastPermission:_rate", "ActivityManager:_rate"]]

print(process_rates)


# Create a scatter plot of the event rates
plt.figure(figsize=(10, 8))
sns.scatterplot(x='SendBroadcastPermission:_rate', y='ActivityManager:_rate', data=event_counts_pivot)
plt.title("Event Rates: SendBroadcastPermission vs ActivityManager")
plt.xlabel("SendBroadcastPermission Event Rate (events per minute)")
plt.ylabel("ActivityManager Event Rate (events per minute)")
plt.show()

# Fit a linear regression model
model = ols('ActivityManager:_rate ~ SendBroadcastPermission:_rate', data=event_counts_pivot).fit()

# Print the summary of the model
print(model.summary())

# Plot the residuals
plt.figure(figsize=(10, 8))
sns.scatterplot(x='SendBroadcastPermission:_rate', y=model.resid, data=event_counts_pivot)
plt.axhline(0, color='red', linestyle='--')  # Add a horizontal line at y = 0
plt.title("Residuals of the Model")
plt.xlabel("SendBroadcastPermission Event Rate (events per minute)")
plt.ylabel("Residuals")
plt.show()











"""
Citation:
Jieming Zhu, Shilin He, Pinjia He, Jinyang Liu, Michael R. Lyu. [Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics](https://arxiv.org/abs/2008.06448). IEEE International Symposium on Software Reliability Engineering (ISSRE), 2023.
"""