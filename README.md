# Corral QAI Experiment

This repo contain a big dataset (more than 4000 observations) of public fragments
of python code extracted from: [Pastebin](http://pastebin.com/),
[Gist](https://gist.github.com/) and [ActiveState](http://code.activestate.com/).
Used for estimate the most common number of errors of **any** python file (tau).

This value is used as default tolerance for the
[Corral](https://github.com/toros-astro/corral)
Quality Assurance Index (QAI).

Yo can see more about this in the paper:
[Astronomical Data Processing Through Model-View-Controller Inspired Architecture]()

## 1. Files:

- `requirements.txt`: before run anything yo need to run

        $ pip install -r requirements.txt

- `corral_qai.py`: Data Collector utility. This file extract data from a
  data-source and dump into a [SQLite](https://www.sqlite.org/) db.
- `metrics.py`: Create a [Pandas](http://pandas.pydata.org/) dataframe from
  the SQLite DB.
- `settings.py.template`: *settings.py* template needed to run
  *corral_qai.py*
- `Makefile`: Gnu-Make routines
- `analysis.ipynb`: the experiment for determine tau.


## 2. Data

- The data are distributed in two formats a
  [CSV](https://en.wikipedia.org/wiki/Comma-separated_values)
  `data/corral_qai.csv` and SQLite Dump `corral_qai.sql`

### 2.1. Description

The csv and the sql file attributes:

- `id`: internal id (integer unique)
- `timestamp`: date and time of the observation (datetime)
- `response`: the full dump of the retrieved data for this observation (text)
- `source`: gist, pastebin or active state (text)
- `source_id`: id used internally of the source (text)
- `description`: description of the file (text)
- `file_name`: name of the file (text)
- `file_sha512`: hash of the file (unique)
- `file_raw_url`: where to find the original data (text)
- `file_size`: size in bytes of the file (integer)
- `file_content`: the full content of the file encoded in utf-8 (text)
- `flake8_output`: full output of the [flake8](http://flake8.pycqa.org)
  analysis over the file (text)
- `flake8_errors`: number of errors found by flake8 (integer)


## 4. Citation

If you are interested in use this dataset in your research please cite us as

    > foo fo fo

Or in [bibtext](http://www.bibtex.org/)

```bibtext
```


## 3. Disclaimer

All information here are made public by their authors.





