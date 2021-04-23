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
- `npm v6.14.12`, [this may help](https://github.com/nodejs/help/wiki/Installation#how-to-install-nodejs-via-binary-archive-on-linux)
- `openvswitch-switch v2.9.8` 

Install the internal packages:
Ensure you are within this directory: `cd haoc21-ae`
```
python3 -m pip install -r requirements.txt
npm install vega-lite vega-cli canvas
```

### Reproduce the experiements
First copy over the script into the reckon folder and then build the container.
Building the container may take some time to complete (~30 mins at most)
```
cp reckon_script.py reckon/haoc.py
./update_reckon_dockerfile.sh
cd reckon
make run
```

`make run` should have placed you within the reckon container.
Now you can execute the script to run the tests.

If you want to run all the tests (~1 hour):
```
python3 ./haoc.py -l
```

If you want to just run the traces (~20 mins):
```
python3 ./haoc.py
```

Exit the contianer and return to this directory:
```
Ctrl - C
cd ..
```

Copy the data out of the container, preprocess it and plot the figures:
```
docker cp reckon:/results ./results
./get_bandwidth.sh
mkdir figures
python3 ./plot_results.py
```

If there are any tests which aren't run, the script will say that the relevant file is missing.
