# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
 Authors: 

 Usage example:
   - <Script>
"""
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
