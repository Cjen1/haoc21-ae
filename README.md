# haoc21-ae

This repo contains the scripts necessary to reproduce the HAOC 21 reckon paper

# Steps

## Getting the data
Run the following commands:
- copy over the script into the reckon folder
  - `cp reckon_script.py reckon/script.py`
- Build and enter the docker container environment (This may take quite a while the first time)
  - `cd reckon`
  - `make docker`
- Within the reckon container execute the script to run all the tests (This will take quite a while unfortunately)
  - `python3 ./script.py`
- Exit the container and return to this directory
- Copy the data out of the container
  - `docker cp reckon:/results ./results`
- Generate bandwidth values from pcap files
  - `./get_bandwidth.sh`
- Create the figure direcotry and make the graphs
  - `mkdir figures`
  - `python3 ./plot_results.py`
