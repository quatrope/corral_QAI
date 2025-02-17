# Corral QAI Experiment

This repo contains a big dataset (more than 4,000 observations) of public fragments
of python code extracted from: [Pastebin](http://pastebin.com/),
[Gist](https://gist.github.com/) and [ActiveState](http://code.activestate.com/).
These are used to estimate the most common number of errors of **any** python file (tau).

This value is used as default tolerance for the
[Corral](https://github.com/toros-astro/corral)
Quality Assurance Index (QAI).

Yo can see more about this in the paper:
[Astronomical Data Processing Through Model-View-Controller Inspired Architecture]()

## 1. Files:

- `requirements.txt`: before running anything, you need to run

        $ pip install -r requirements.txt

- `corral_qai.py`: Data Collector Utility. This file extracts data from a
  data-source and dumps into a [SQLite](https://www.sqlite.org/) database.
- `metrics.py`: Creates a [Pandas](http://pandas.pydata.org/) dataframe from
  the SQLite database.
- `settings.py.template`: *settings.py* template needed to run
  *corral_qai.py*
- `Makefile`: Gnu-Make routines
- `analysis.ipynb`: the experiment to determine tau.


## 2. Data

- The data are distributed in two formats: a
  [CSV](https://en.wikipedia.org/wiki/Comma-separated_values)
  `data/corral_qai.csv` and a SQLite Dump `corral_qai.sql`

### 2.1. Description

The csv and the sql file attributes are:

- `id`: internal id (integer unique)
- `timestamp`: date and time of the observation (datetime)
- `response`: the full dump of the retrieved data for this observation (text)
- `source`: gist, pastebin or active state (text)
- `source_id`: id used internally for the source (text)
- `description`: a description of the file (text)
- `file_name`: name of the file (text)
- `file_sha512`: hash of the file (unique)
- `file_raw_url`: where to find the original data (text)
- `file_size`: size in bytes of the file (integer)
- `file_content`: the full content of the file encoded in utf-8 (text)
- `flake8_output`: full output of the [flake8](http://flake8.pycqa.org)
  analysis over the file (text)
- `flake8_errors`: number of errors found by flake8 (integer)


## 4. Citation

If you are interested in using this dataset in your research please cite us as

    > foo fo fo

Or in [bibtext](http://www.bibtex.org/)

```bibtext
```


## 3. Disclaimer

All information here is made public by their authors.





