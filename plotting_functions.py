import pandas as pd
import numpy as np

import altair as alt
from altair import datum

alt.data_transformers.enable('default')
alt.data_transformers.disable_max_rows()

def read_in_res(file, parameters):
    print(file)
    df = pd.read_json(file)
    df['latency'] = (df['End'] - df['Cli_start']) * 1000
    df['time'] = df['End']
    df = df.sort_values("time")
    df['achieved_rate'] = df['End'].count() / (df['End'].max() - df['End'].min())
    for parameter, value in parameters.items():
        df[parameter] = value
    return df

def summarise_run(file):
    df = pd.read_json(path_or_buf=filepath, orient="records")

    length = df["End"].max() - df["End"].min()
    throughput = len(df["End"]) / length
    print("Throughput for {} = {}".format(filepath, throughput))
    print("Latency for {} =".format(filepath))
    df = df["End"] - df["Cli_start"]
    print(df.describe(percentiles=[0.25, 0.50, 0.75, 0.99], include="all"))
    
def normalise_times(df, time_p, groupby):
    def process_group(group):
        group[time_p] = group[time_p] - group[time_p].min()
        return group
    return df.groupby(groupby, sort=False).apply(process_group)

def default_if_error(f, d):
    try:
        return f ()
    except Exception as e:
        print(e)
        return d

def divide_windows(df, time_p, window_size=1):
    df = df.sort_values(by=time_p)
    
    res = []
    
    lats = []
    cw = df[time_p].min()
    cnt = 0
    for _, row in df.iterrows():
        cnt += 1
        if cnt % 10000 == 0:
            print('.')
            
        while row[time_p] > cw + window_size:
            res += [{'time':cw, 'latencies':lats}]
            lats = []
            cw += window_size
        
        lats += [row['latency']]
        
    res += [{'time':cw, 'latencies':lats}]
    return res