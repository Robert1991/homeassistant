#!/usr/local/bin/python
# coding: utf8

with open('/config/.HA_VERSION') as data_file:
    print(data_file.readline())
