# haoc21-ae

This repo contains the scripts necessary to reproduce the HAOC 21 reckon paper.

## System requirements
This has been tested working on the following hardware:
- 192GB RAM
- 32 core CPU
- 1TB hard drive

However we expect that the following should be sufficient if change the `tmpfs` mount in reckon to be a bind mount instead (this was used in the paper for more realistic validation results).
- 32GB RAM
- 8 core CPU
- ~50GB hard drive space

## Steps

### Cloning the repository
`git clone --recurse-submodules https://github.com/Cjen1/haoc21-ae.git`

### Prerequisites
We need the following packages installed with these versions:
- `python v3.6.9` and `pip`
- `npm v6.14.12`, [this may help]{https://github.com/nodejs/help/wiki/Installation#how-to-install-nodejs-via-binary-archive-on-linux}
- `openvswitch-switch v2.9.8` 

Install the internal packages:
- Ensure you are within this directory: `cd haoc21-ae`
- `python3 -m pip install -r requirements.txt`
- `npm install vega-lite vega-cli canvas`

### Reproduce the experiements
Run the following commands:
- copy over the script into the reckon folder
  - `cp reckon_script.py reckon/haoc.py`
- Build and enter the docker container environment (This may take quite a while the first time)
  - `./update_reckon_dockerfile.sh`
  - `cd reckon`
  - `make run`
- The final `make run` should have placed you within the reckon container. Now execute the script to run all the tests (This may take up to a couple of hours). Additionally running concurrent workloads in not a massive issue since the traces in the paper should not pin the CPU.
  - `python3 ./haoc.py`
- Exit the container and return to this directory
- Copy the data out of the container
  - `docker cp reckon:/results ./results`
- Generate bandwidth values from pcap files
  - `./get_bandwidth.sh`
- Create the figure direcotry and make the graphs
  - `mkdir figures`
  - `python3 ./plot_results.py`
