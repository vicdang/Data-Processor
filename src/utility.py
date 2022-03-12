# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
---------------------------
Copyright (C) 2021
@Authors: vudnn.dl@gmail.com
@Date: 30-Dec-21
@Version: 1.0
---------------------------
 Usage example:
   - utility.py <options>

"""
import collections
import logging
logger = logging.getLogger(__name__)

def get_config():
   """
   Using to get the configuration
   :return:
   """
   try:
      from configparser import ConfigParser
   except ImportError:
      from ConfigParser import ConfigParser  # ver. < 3.0
   # instantiate
   conf = ConfigParser()
   # parse existing file
   conf.read('./config/config.ini')
   return conf

def slice_data(data, groups, **kwargs):
   """
   Used to slice data
   :param data:
   :param groups:
   :return:
   """
   rev_before = kwargs.get('rev_before', 0)
   items = data.items()
   dt = collections.OrderedDict(sorted(items))
   max_val = int(list(dt.keys())[-1])
   g = groups - rev_before
   start = rev_before
   fn = g
   end = groups - 1
   s = 0
   gp = {}
   while True:
      gp.update({"%d-%d" % (start, end): dict(list(sorted(items))[s: fn])})
      start = end + rev_before + 1
      s = fn
      fn = s + g
      end = end + int(groups) if end + int(groups) < max_val else max_val
      if start >= max_val:
         break
   return gp
