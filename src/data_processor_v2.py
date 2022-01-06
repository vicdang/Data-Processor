# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
---------------------------
Copyright (C) 2021
@Authors: dnnvu
@Date: 30-Dec-21
@Version: 1.0
---------------------------
 Usage example:
   - data_processor_v2.py <options>

"""

import logging
import sys
import re
import copy

import utility as util
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class DataProcessor(object):
   """docstring for DataProcessor"""

   def __init__(self, *args, **kwargs):
      self.conf = kwargs.get('config', util.get_config())
      super(DataProcessor, self).__init__()
      self.arg = kwargs.get('arg', None)
      data = kwargs.get('data', None)
      self.dp = pd.DataFrame(data)
      pd.set_option('display.max_columns', None)
      self.avg_d_ut = self.avg_v_d_ut = self.avg_c_v_d_ut = self.avg_v_z = \
         [0, 0, 0]
      self.avg_z = 0
      self.dut = self.z = self.v_d_ut_tmp = self.slop = self.intercept = []
      self.d_theta = self.dp
      self.rect_count = self.conf.get("general", "rect_count")
      self.col_r = self.conf.get("general", "col_r")
      self.col_z = self.conf.get("general", "col_z")
      self.col_theta = self.conf.get("general", "col_theta")

   def get_avg_delta_ut(self):
      ut0 = float(self.dp.loc['{col}.1'.format(col=str(self.col_r))])
      for r in range(int(self.rect_count)):
         self.dut.append(float(self.dp.loc['%s.%d' % (self.col_theta, r + 1)])*
                    float(self.dp.loc[('%s.%d' % (self.col_r, r + 1))]) - ut0)
      self.avg_d_ut = self.get_avg([self.dut[:12], self.dut[12],
                                    self.dut[12:]])

   def get_avg_var_delta_ut(self):
      v_d_ut = []
      for r in range(int(self.rect_count)):
         var = self.dut[r] - self.avg_d_ut[self.get_layer(r)]
         v_d_ut.append(var**2)
         self.v_d_ut_tmp.append(var)
      self.avg_v_d_ut = self.get_avg([v_d_ut[:12], v_d_ut[12], v_d_ut[12:]])

   def get_avg_co_var_delta_ut(self):
      c_v_d_ut = []
      for r in range(int(self.rect_count)):
         c_v_d_ut.append((self.v_d_ut_tmp[r]) * (self.z[r] - self.avg_z[
            self.get_layer(r)]))
      self.avg_c_v_d_ut = self.get_avg([c_v_d_ut[:12], c_v_d_ut[12],
                                        c_v_d_ut[12:]])

   def get_avg_z(self):
      for r in range(int(self.rect_count)):
         self.z.append(float(self.dp.loc['%s.%d' % (self.col_z, r + 1)]))
      self.avg_z = self.get_avg([self.z[:12], self.z[12], self.z[12:]])

   def get_avg_v_z(self):
      v_z = []
      for r in range(int(self.rect_count)):
         v_z.append((self.z[r] - self.avg_z[self.get_layer(r)])**2)
      self.avg_v_z = self.get_avg([v_z[:12], v_z[12], v_z[12:]])

   def get_layer(self, row):
      if row < 12:
         layer = 0
      elif row == 12:
         layer = 1
      else:
         layer = 2
      return layer

   def get_slop(self):
      i = 0
      for item in self.avg_c_v_d_ut:
         if self.avg_v_z[i] != 0:
            self.slop.append(item / self.avg_v_z[i])
         else:
            self.slop.append(0)
         logger.info("item")
         logger.info(item)
         i += 1

   def get_intercept(self):
      i = 0
      for item in self.avg_c_v_d_ut:
         self.intercept[i] = item - (self.avg_z[i]) * (self.slop[i])
         i += 1

   def filter_data(self, index,
                   regex='([a-zA-Z]+ \[mm\]|\[rad\]|\(cylinder\))'):
      return self.dp.filter(regex=regex)

   @staticmethod
   def get_avg(data):
      """
      Average
      :param data:
      :return:
      """
      if type(data) in [list, tuple, pd.Series]:
         r = []
         for d in data:
            r.append(np.average(d))
         return r
      else:
         return np.average(data)

   def add_col(self, col_name, data=""):
      """
      Add new column(s) into the data
      :param col_name:
      :param data:
      """
      if isinstance(col_name, list):
         for col in col_name:
            self.dp[str(col)] = data
      else:
         self.dp[str(col_name)] = data

   def run(self):
      self.get_avg_delta_ut()
      self.get_avg_var_delta_ut()
      self.get_avg_z()
      self.get_avg_v_z()
      self.get_avg_co_var_delta_ut()
      self.get_slop()
      logger.info("slop")
      logger.info(self.slop)
      logger.info(len(self.slop))
      # self.get_intercept()
      # logger.info("intercept")
      # logger.info(self.intercept)
      return

def main(args):
   """
   Main process
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
