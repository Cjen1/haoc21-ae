#!/usr/bin/env bash

for file in results/*bandwidth.pcap
do
	./pcap_bw.py $file 10.0.0.1 10.0.0.2 10.0.0.3 10.0.0.4 > $file.throughput 
done 
