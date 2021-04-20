# Install requirements

Python 3.8.3 required

Install requirements with:
```
pip install -r requirements.txt
```

# Team Members

- Kevin Nguyen
- Cassandra Patterson

# Run example:

```
> python .\main.py -h
usage: main.py [-h] input seed

Event Simulator

positional arguments:
  input       Input file for simulation
  seed        Seed number for simulation

optional arguments:
  -h, --help  show this help message and exit
```

```
python ./main.py ./input.1 2
```

# Outputs

Outputs will be printed to stdout after simulation completes. The response time and various metrics associated with it (mean, min, max, percentiles, etc.) will be shown at the bottom, with other statistics of interest printed above.

In addition, two plots will be generated and written to file based on the input file name and the seed number. 

The one ending in "*scatter.png" will display a scatter plot of all FileRecievedEvents response times, the y-axis displaying the response time for that event.
The x-axis for this scatterplot does not have any significant information, and only shows the index/order the plot point was recorded. The red points indicate a cache miss, while the blue points are cache hits.

The one ending in "*hist.png" is a histogram of the response times.