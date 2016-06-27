# Corral QAI Experiment

This repo contain a big dataset (more than 4000 observations) of public fragments
of python code extracted from: [Pastebin](http://pastebin.com/),
[Gist](https://gist.github.com/) and [ActiveState](http://code.activestate.com/).
Used for estimate the most common number of errors of **any** python file (tau).

This value is used as default tolerance for the [Corral](https://github.com/toros-astro/corral)
Quality Assurance Index (QAI).

Yo can see more about this in the paper:
[Astronomical Data Processing Through Model-View-Controller Inspired Architecture]()

## Files:

- `corral_qai.py`: Data Collector utility. This file extract data from a
  datasource and dump into a [SQLite]() db.
- `metrics.py`: Create a [Pandas]() dataframe from the SQLitedb.
- `settings.py.template`: *settings.py* template needed to run
  *corral_qai.py*
- `requirements.txt`: before run anything yo need to run

      ```console
      $ pip install -r requirements.tx
      ```
- `Makefile`: Gnu-Make routines
- `analysis.ipynb`: the experiment for determine tau.


## Data

- The data are distributed in two formats a [CSV]()
  `data/corral_qai.csv` and SQLite Dump `corral_qai.sql`


## Disclaimer

All information here are made public by their authors.



