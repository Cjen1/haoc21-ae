import pandas as pd
import numpy as np
import altair as alt
from altair import datum
from datetime import datetime
import altair_saver as alts

import plotting_functions as pf


# ---- Failure analysis --------------------------- 
repeats = 1

def variable_mapping(var, mapping, exceptions = []):
    if var in exceptions:
        return var
    [src,dst] = var.split(':')
    src = mapping[src]
    dst = mapping[dst]
    if src <= dst:
        return (src + '-' + dst)
    else:
        return (dst + '-' + src)

def not_self(name, exceptions=[]):
    if name in exceptions: return True
    [src,dst] = name.split('-')
    return src != dst

def success_rate(lat, threshold):
    yes = lat[lat < threshold]
    return yes.count()[0]

def preprocess(res, bw, mapping):
    df_res = pf.read_in_res(res, {})
    df_bw = pd.read_csv(bw)
    
    time_p = 'Cli_start'
    
    starttime = df_res[time_p].min()
    
    # BW preprocessing 
    df_bw['time'] = df_bw['# time']
    df_bw = df_bw.drop('# time', axis=1)
    df_bw = df_bw.melt(id_vars=['time'])
    
    df_bw['time'] = df_bw['time'] - starttime
    
    df_bw['value'] = df_bw['value'] / 1000000
    df_bw['variable'] = df_bw['variable'].apply(lambda var : variable_mapping(var, mapping, exceptions=['totalbw']))
    df_bw = df_bw.groupby(by=['time','variable'], as_index=False).sum()
    df_bw = df_bw[df_bw['variable'].apply(lambda var : not_self(var, exceptions=['totalbw']))]
    
    # Res preprocessing
    df_res[time_p] = df_res[time_p] - starttime
    window_size=0.1
    df_rate = pd.DataFrame(pf.divide_windows(df_res, time_p, window_size=window_size))
        
    df_rate['success_rate'] = df_rate.apply(lambda row: success_rate(pd.DataFrame(row['latencies']), 100), axis=1) / window_size
    
    return df_rate, df_bw

def plot_rate_bw(rate, bw, yinnerdomain, yclientdomain, use_legend, xdomain=None, rate_height=60, bw_height=40):
    rate_chart = alt.Chart(rate).mark_line(color='#5e6472', clip=True).encode(
        x=alt.X('time', axis=alt.Axis(title='', labels=False), scale=alt.Scale(nice=False, domain=xdomain)),
        y=alt.Y('success_rate:Q', axis=alt.Axis(title=['Success','rate (s⁻¹)'])),
    ).properties(height=rate_height)
    
    client_comm = bw.apply(lambda row: 'Client' in row['variable'], axis=1)
    
    bw_inner_chart = alt.Chart(bw[~client_comm]).mark_line(clip=True).encode(
        x=alt.X("time", axis=alt.Axis(title='', labels=False), scale=alt.Scale(nice=False, domain=(
            [0, bw['time'].max()] if xdomain == None else xdomain
        ))),
        y=alt.Y("value", axis=alt.Axis(title=''), scale=alt.Scale(domain=yinnerdomain)),
        color=alt.Color('variable', legend=(alt.Legend(title=['Traffic','Direction']) if use_legend else None)),
        strokeDash=alt.StrokeDash('variable', legend=None)
    ).properties(height=bw_height)
    
    bw_client_chart = alt.Chart(bw[client_comm]).mark_line(clip=True).encode(
        x=alt.X("time", axis=alt.Axis(title='Timestamp (s)'), scale=alt.Scale(nice=False, domain=(
            [0, bw['time'].max()] if xdomain == None else xdomain
        ))),
        y=alt.Y("value", axis=alt.Axis(title=''), scale=alt.Scale(domain=yclientdomain)),
        color=alt.Color('variable', legend=(alt.Legend(title='') if use_legend else None)),
        strokeDash=alt.StrokeDash('variable', legend=None)
    ).properties(height=bw_height)
    
    upper = rate_chart
    lower = alt.vconcat(
        bw_inner_chart, bw_client_chart, 
        title = alt.TitleParams(
            'Bandwidth (MB/s)',
            orient='left',
            anchor='middle',
            dx=15
        )
    ).resolve_scale(color='shared', strokeDash='independent')
    
    return alt.vconcat(upper,lower).resolve_scale(x=alt.ResolveMode('shared'))


def leader_plot():
    print("Plotting leader")
    mapping = {"10.0.0.1": "10.0.0.1", "10.0.0.2": "10.0.0.2", "10.0.0.3": "10.0.0.3", "10.0.0.4": "Client"}
    chart = alt.vconcat()
    for repeat in range(repeats):
        lr = f"results/res_etcd.simple.go.leader.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.res"
        lb = f"results/pcap_etcd.simple.go.leader.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.pcap.throughput"
        lr,lb = preprocess(lr,lb, mapping)
        chart = alt.vconcat(chart, plot_rate_bw(lr,lb, (0,2), (0, 0.5), True, xdomain=(0,60)))
    alts.save(chart, "figures/leader.pdf")

def partial_partition_plot():
    print("Plotting partial partition")
    mapping = {"10.0.0.1": "10.0.0.1", "10.0.0.2": "10.0.0.2", "10.0.0.3": "10.0.0.3", "10.0.0.4": "Client"}
    chart = alt.vconcat()
    for repeat in range(repeats):
        lr = f"results/res_etcd.simple.go.partial-partition.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.res"
        lb = f"results/pcap_etcd.simple.go.partial-partition.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.pcap.throughput"
        lr,lb = preprocess(lr,lb, mapping)
        chart = alt.vconcat(chart, plot_rate_bw(lr,lb, (0,2), (0, 0.5), True, xdomain=(0,60)))
    alts.save(chart, "figures/partial_parition.pdf")

def pre_vote_partition_plot():
    print("Plotting pre-vote partial partition")
    mapping = {"10.0.0.1": "10.0.0.1", "10.0.0.2": "10.0.0.2", "10.0.0.3": "10.0.0.3", "10.0.0.4": "Client"}
    chart = alt.vconcat()
    for repeat in range(repeats):
        lr = f"results/res_etcd-pre-vote.simple.go.partial-partition.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.res"
        lb = f"results/pcap_etcd-pre-vote.simple.go.partial-partition.nn_3.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.pcap.throughput"
        lr,lb = preprocess(lr,lb, mapping)
        chart = alt.vconcat(chart, plot_rate_bw(lr,lb, (0,2), (0, 0.5), True, xdomain=(0,60)))
    alts.save(chart, "figures/pre_vote_partition.pdf")

def intermittent_full_plot():
    print("Plotting intermittent full partition")
    print("WARNING: This plot can crash the plotting software since it has too many data points, it can however be extracted via the jupyter notebook interface")
    mapping = {"10.0.0.1": "10.0.0.1", "10.0.0.2": "10.0.0.2", "10.0.0.3": "10.0.0.3", "10.0.0.4": "Client"}
    chart = alt.vconcat()
    for repeat in range(repeats):
        lr = f"results/res_etcd.simple.go.intermittent-full.nn_3.nc_1.write_ratio_1.mtbf_10.rate_1000.duration_600.tag_repeat-{repeat}-bandwidth.res"
        lb = f"results/pcap_etcd.simple.go.intermittent-full.nn_3.nc_1.write_ratio_1.mtbf_10.rate_1000.duration_600.tag_repeat-{repeat}-bandwidth.pcap.throughput"
        lr,lb = preprocess(lr,lb, mapping)
        chart = alt.vconcat(chart, plot_rate_bw(lr,lb, (0,2), (0, 0.5), True, xdomain=(0,600)))
    alts.save(chart, "figures/intermittent_full.pdf")

def achieved_rate_preprocess(df):
    def percentile(n):
        def percentile_(x):
            return x.quantile(n)
        percentile_.__name__ = 'percentile_{:2.0f}'.format(n*100)
        return percentile
    
    df['lat_cli'] = (df['End'] - df['Cli_start']) * 1000
    
    summaries_non_melt = df.groupby(['n_servers', 'achieved_rate', 'rate', 'repeat'])['lat_cli'].describe(percentiles=[0.01, 0.5,0.99])
    summaries_non_melt = summaries_non_melt.reset_index().rename(columns={'1%':"p1", '50%':'p50', '99%':'p99'})
    print(summaries_non_melt)
    #res = pd.melt(summaries_non_melt, id_vars=['achieved_rate', 'repeat', 'rate'], value_vars=['p1', 'p50', 'p99'], var_name='percentile', value_name='latency')
    res = summaries_non_melt
    
    return res

def achieved_rate_plot(res, height):
    base = alt.Chart(res).transform_calculate(
        rate_error = ((datum.achieved_rate / datum.rate) - 1),
        rate_error_abs = (datum.rate_error * datum.rate_error)
    ).transform_filter(
        (datum.rate_error_abs < 0.001)
    ).encode(
        x=alt.X('achieved_rate:Q', axis=alt.Axis(title='Achieved Rate (req/s)'), scale=alt.Scale(domain=(0,24000))),
        y=alt.Y(axis=alt.Axis(title='Latency (ms)'), scale=alt.Scale(type='log', domain=(1,300), nice=False)),
        order = 'rate',
        color=alt.Color('n_servers:N', legend=alt.Legend(title=['Number','of servers']))
    )
  
    median = base.mark_line(point=True, clip=True).encode(
        y=alt.Y('p50', axis=alt.Axis(title='Latency (ms)'), scale=alt.Scale(type='log', domain=(1,300), nice=False)),
    ).properties(height=height)
    
    p99 = base.mark_line(clip=True, strokeDash=[5,2]).encode(
        y='p99',
    )
    
    return (median + p99)

def cdf(data):
    data = np.sort(data['latency'])
    n_points = 100
    ptiles = np.linspace(0,1,n_points)
    values = np.quantile(data, ptiles)

    df = pd.DataFrame.from_dict({'percentile':ptiles, 'latency': values})
    
    return df

def process(group, grouping_parameters, f):
    print(grouping_parameters)
    res = f(group)
    res = pd.DataFrame(res)
    for p,v in grouping_parameters.items():
        res[p] = v
    return res

def validation_plot():
    # Rate Latency
    validation_data = pd.concat([
        pf.read_in_res(
            f"results/res_etcd.simple.go.none.nn_{n_servers}.nc_1.write_ratio_1.mtbf_1.rate_{rate}.duration_60.tag_repeat-{repeat}.res",
            {'repeat':repeat, 'rate':rate,'n_servers':n_servers}
        )
        for rate in [1,2000,4000,6000,8000,10000,12000,14000,16000,18000,20000,22000,24000,26000,28000,30000]
        for n_servers in [3,5,7,9]
        for repeat in range(repeats)
    ], ignore_index=True)

    
    rate_lat_res = achieved_rate_preprocess(validation_data)
    
    df = rate_lat_res
    chart = alt.vconcat()
    for repeat in range(repeats):
        chart = alt.vconcat(chart, achieved_rate_plot(df[df['repeat'] == repeat], 100))
    alts.save(chart, "figures/validation_rate_latency.pdf")

    # CDF
    cdf_data = validation_data
    cdf_data = cdf_data[cdf_data['rate'] == 10000]

    group_by = ['n_servers', 'repeat']
    cdfs = pd.concat([
        process(group, dict(zip(group_by, params)), lambda group: cdf(group))
        for params, group in cdf_data.groupby(group_by)
    ])
    
    chart = alt.vconcat()
    for repeat in range(repeats):
        rep_chart = alt.Chart(cdfs).mark_line(clip=True).encode(
            x=alt.X('latency:Q', axis=alt.Axis(title='Latency (ms)'), scale=alt.Scale(domain=[0,100])),
            y=alt.Y('percentile:Q', axis=alt.Axis(title='Cumulative fraction')),
            color=alt.Color('n_servers:N', legend=None)
        ).properties(height=130)

        chart = alt.vconcat(chart, rep_chart)
    
    alts.save(chart, "figures/validation_cdf.pdf")
    
def wan_plot():
    chart = alt.vconcat()
    for repeat in range(repeats):
        wan_data = pf.read_in_res(
            f"results/res_etcd.wan.go.none.nn_7.nc_1.write_ratio_1.mtbf_1.rate_1000.duration_60.tag_repeat-{repeat}-bandwidth.res",
            {'repeat':repeat}
        )
    
        cdf_wan = cdf(wan_data)
    
        rep_chart = alt.Chart(cdf_wan).mark_line(clip=True).encode(
            x=alt.X('latency:Q', axis=alt.Axis(title='Latency (ms)'), ),
            y=alt.Y('percentile:Q', axis=alt.Axis(title='Cumulative fraction')),
        ).properties(height=150)
        chart = alt.vconcat(chart, rep_chart)
    
    alts.save(chart, "figures/wan.pdf")


if __name__ == "__main__":
  alt.data_transformers.disable_max_rows()

  leader_plot()
  partial_partition_plot()
  validation_plot()
  wan_plot()
  intermittent_full_plot()
