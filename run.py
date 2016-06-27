#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, datetime

import time
while True:
    print ">>>>>", datetime.datetime.now()
    os.system("make all")
    print "sleeping 1:10", datetime.datetime.now()
    time.sleep(60*60+600)
