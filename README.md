# haoc21-ae

This repo contains the scripts necessary to reproduce the HAOC 21 reckon paper.

## Steps

### Cloning the repository
`git clone --recurse-submodules https://github.com/Cjen1/haoc21-ae.git`

### Setting up the environment
Run the following commands:
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
- Within the reckon container execute the script to run all the tests (This will take quite a while unfortunately)
  - `python3 ./haoc.py`
- Exit the container and return to this directory
- Copy the data out of the container
  - `docker cp reckon:/results ./results`
- Generate bandwidth values from pcap files
  - `./get_bandwidth.sh`
- Create the figure direcotry and make the graphs
  - `mkdir figures`
  - `python3 ./plot_results.py`
