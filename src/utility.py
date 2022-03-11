# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
 Authors: 

 Usage example:
   - <Script>
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
   max = len(data) - 1
   items = data.items()
   dt = collections.OrderedDict(sorted(items))
   gap = int(list(dt.keys())[0])
   start = 0
   end = int(groups) - 1
   gp = {}
   while True:
      gp.update({"%d-%d" % (start + gap, end + gap): dict(list(
            items)[start:end + 1])})
      start = end + 1
      end = end + int(groups) if end + int(groups) < max else max
      if start >= max:
         break
   return gp

