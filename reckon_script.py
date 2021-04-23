from subprocess import call, Popen
import argparse
import shlex
import itertools as it
import numpy as np

def call_tcp_dump(tag, cmd):
    tcp_dump_cmd = [
        "tcpdump",
        "-i",
        "any",
        "-w",
        ("/results/pcap_" + tag + ".pcap"),
        "net",
        "10.0.0.0/16",
        "-n",
    ]
    print(tcp_dump_cmd)
    p = Popen(tcp_dump_cmd)
    call(cmd)
    p.terminate()


def run_test(system='etcd', topo='simple', nn='3', nc='1', write_rate='1', failure='none', mtbf='1', client='go', ncpr='False', rate='1000', duration='60', tag='', write_ratio='1', tcp_dump=True):
    config = {
        "system" : system,
        "topo" : topo,
        "nn" : nn,
        "nc" : nc,
        "write_ratio":write_ratio,
        "failure":failure,
        "mtbf":mtbf,
        "client":client,
        "ncpr":ncpr,
        "rate":rate,
        "duration":duration,
        "tag":tag
        }

    tag = (
            "{system}.{topo}.{client}.{failure}.nn_{nn}.nc_{nc}.write_ratio_{write_ratio}.mtbf_{mtbf}.rate_{rate}.duration_{duration}.tag_{tag}"
        ).format(**config)

    config['tag'] = tag

    cmd = (
            "python benchmark.py {system} {topo} --number-nodes {nn} --number-clients {nc} uniform --write-ratio {write_ratio} " +
            "{failure} --mtbf {mtbf} --client {client} --new_client_per_request {ncpr} --system_logs /results/logs " +
            "--rate {rate} --duration {duration} --result-location /results/res_{tag}.res"
        ).format(**config)

    cmd = shlex.split(cmd)

    
    if tcp_dump:
        call_tcp_dump(tag,cmd)
    else:
        call(cmd)

    call("rm -rf /data/*", shell=True)
    call("mn -c", shell=True)

parser = argparse.ArgumentParser(description = "Run HAOC tests")
parser.add_argument('--repeats', type=int, default = 1, help="The total number of repeats to run.")
parser.add_argument('-l', '--long', action='store_true', help="Runs the validation tests which take a lot longer.")

args = parser.parse_args()

for repeat in range(args.repeats):
    tag = 'repeat-{0}-bandwidth'.format(repeat)
    run_test(failure='leader', tag=tag)
    run_test(failure='partial-partition', tag=tag)
    run_test(system='etcd-pre-vote', failure='partial-partition', tag=tag)
    run_test(failure='intermittent-full', duration='600', mtbf='10', tag=tag)
    run_test(topo='wan', nn='7', tag=tag, tcp_dump=False)
    if args.long:
        tag = 'repeat-{0}'.format(repeat)
        rates = [1, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000, 30000]
        n_servers = [3, 5, 7, 9]
        params = [v for v in it.product(rates, n_servers)]
        np.random.shuffle(params)
        for rate, n_server in params:
            run_test(nn=str(n_server), rate=str(rate), tag=(tag), tcp_dump=False)
