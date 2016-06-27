#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os


import corral_qai

import pandas as pd

from flask_peewee.utils import get_dictionary_from_model

df = pd.DataFrame(map(get_dictionary_from_model, corral_qai.PythonFile.select()))

if __name__ == "__main__":
    tolerance = 1
    if tolerance:
        sigma3 = df.std()["flake8_errors"] * tolerance
        cleaned = df[df.flake8_errors <= sigma3]
    else:
        cleaned = df

    print("{} Sigma Stats".format(tolerance))
    print(cleaned.describe())

    print("-" * 50)
    print("Total: ", df.count().id)
    print("Used: ", cleaned.count().id)



