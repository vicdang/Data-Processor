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
   - data_processor.py <options>

"""
import json
import logging
import math
import sys

import numpy as np
import pandas as pd

import utility as util

logger = logging.getLogger(__name__)

class DataProcessor(object):
   """docstring for DataProcessor"""

   def __init__(self, *args, **kwargs):
      self.conf = kwargs.get('config', util.get_config())
      super(DataProcessor, self).__init__()
      self.arg = kwargs.get('arg', None)
      data = kwargs.get('data', None)
      self.name = kwargs.get('name', None)
      self.dp = pd.DataFrame(data)
      pd.set_option('display.max_columns', None)
      self.avg_delta_uts = [0, 0, 0]
      self.avg_variance_delta_uts = [0, 0, 0]
      self.avg_co_variance_delta_uts = [0, 0, 0]
      self.avg_variance_zs = [0, 0, 0]
      self.avg_zs = []
      self.delta_uts = []
      self.z = []
      self.variance_delta_ut_temp = []
      self.slops = []
      self.intercepts = []
      self.avg_ms = []
      self.avg_as = []
      self.R2s = []
      self.deformations = []
      self.interface = None
      self.F = None
      self.modales = []
      self.moyenne = None
      self.d_theta = self.dp
      self.rect_count = self.conf.getint("general", "rect_count")
      self.col_r = self.conf.get("general", "col_r")
      self.col_z = self.conf.get("general", "col_z")
      self.col_dtheta = self.conf.get("general", "col_dtheta")
      self.time_field = self.conf.get("general", "time_field")
      self.dev = self.conf.get("general", "dev")
      self.F_convert = self.conf.getint("analysis", "F_convert")
      self.F = float(self.dp.loc["%s" % self.dev]) * self.F_convert
      self.time = float(self.dp.loc["%s" % self.time_field])

   def get_avg_delta_uts(self):
      """
      Used to get AVG(delta ut),
      returns list of AVG(delta ut) by layer (L0, L1, L2)
      """
      ut0 = float(self.dp.loc['{col}.1'.format(col=str(self.col_r))])
      for row in range(int(self.rect_count)):
         t = self.dp.loc['%s.%d' % (self.col_dtheta, row + 1)]
         r = self.dp.loc[('%s.%d' % (self.col_r, row + 1))]
         if row == 0:
            ut0 = 0
         u = float(t) * \
             float(r) - ut0
         self.delta_uts.append(u)
      self.avg_delta_uts = self.get_avg(
            [self.delta_uts[:12], self.delta_uts[12],
             self.delta_uts[12:]])

   def get_avg_variance_delta_uts(self):
      """
      Used to get AVG(variance delta ut),
      returns list of AVG(variance delta ut) by layer (L0, L1, L2)
      """
      variance_delta_ut = []
      v = []
      for row in range(int(self.rect_count)):
         u = self.delta_uts[row]
         du = self.avg_delta_uts[self.get_layer(row)]
         var = u - du
         variance_delta_ut.append(pow(var, 2))
         self.variance_delta_ut_temp.append(var)
      self.avg_variance_delta_uts = self.get_avg(
            [variance_delta_ut[:12], variance_delta_ut[12],
             variance_delta_ut[12:]])

   def get_avg_co_variance_delta_uts(self):
      """
      Used to get AVG(co variance delta ut),
      returns list of AVG(co variance delta ut) by layer (L0, L1, L2)
      """
      co_variance_delta_ut = []
      for row in range(int(self.rect_count)):
         co_variance_delta_ut.append(
               (self.variance_delta_ut_temp[row]) * (self.z[row] - self.avg_zs[
                  self.get_layer(row)]))
      self.avg_co_variance_delta_uts = self.get_avg(
            [co_variance_delta_ut[:12], co_variance_delta_ut[12],
             co_variance_delta_ut[12:]])

   def get_avg_zs(self):
      """
      Used to get AVG(z), returns list of AVG(z) by layer (L0, L1, L2)
      """
      for row in range(int(self.rect_count)):
         self.z.append(float(self.dp.loc['%s.%d' % (self.col_z, row + 1)]))
      self.avg_zs = self.get_avg([self.z[:12], self.z[12], self.z[12:]])

   def get_avg_variance_zs(self):
      """
      Used to get AVG(variance Z), returns list of AVG(variance Z) by layer
      """
      variance_z = []
      for row in range(int(self.rect_count)):
         variance_z.append((self.z[row] - self.avg_zs[self.get_layer(row)])**2)
      self.avg_variance_zs = self.get_avg(
            [variance_z[:12], variance_z[12], variance_z[12:]])

   def get_avg_ms(self):
      """
      Used to get AVG(m), returns list of AVG(m) by layer (L0, L1, L2)
      """
      m = []
      for row in range(int(self.rect_count)):
         layer = self.get_layer(row)
         m.append(self.slops[layer] * self.z[row] + self.intercepts[layer])
      self.avg_ms = self.get_avg([m[:12], m[12], m[12:]])

   def get_avg_as(self):
      """
      Used to get AVG(a), returns list of AVG(a) by layer (L0, L1, L2)
      """
      a = []
      for row in range(int(self.rect_count)):
         layer = self.get_layer(row)
         a.append((self.slops[layer] * self.z[row] + self.intercepts[layer] -
                   self.avg_ms[layer])**2)
      self.avg_as = self.get_avg([a[:12], a[12], a[12:]])

   # Normal calculations
   def get_slops(self):
      """
      Used to get slop valuse, returns list of slop values by layer
      """
      i = 0
      for avg_co_variance_delta_ut in self.avg_co_variance_delta_uts:
         if self.avg_variance_zs[i] != 0:
            self.slops.append(
               avg_co_variance_delta_ut / self.avg_variance_zs[i])
         else:
            self.slops.append(0)
         i += 1

   def get_intercepts(self):
      """
      Used to get Intercept values, returns list of intercept values by layer
      """
      i = 0
      for avg_delta_ut in self.avg_delta_uts:
         self.intercepts.append(
            avg_delta_ut - (self.avg_zs[i] * self.slops[i]))
         i += 1

   def get_R2s(self):
      """
      Used to get the R^2 values, returns list of R^2 values by layer
      """
      i = 0
      for a in self.avg_as:
         self.R2s.append(a / self.avg_variance_delta_uts[i])

   def get_deformations(self):
      """
      Used to get the deformation values, returns list of deformations by layer
      """
      for slop in self.slops:
         self.deformations.append((slop * pow(10, 6)) / 2)

   def get_interface(self):
      """
      Used to get the interface value
      """
      self.interface = ((self.slops[0] * self.z[12]) + self.intercepts[0]) - \
                       ((self.slops[2] * self.z[12]) + self.intercepts[2])

   # Basic calculations
   @staticmethod
   def get_layer(row):
      """
      Used to convert frame id to layer id
      :param row:
      :return:
      """
      if row < 12:
         layer = 0
      elif row == 12:
         layer = 1
      else:
         layer = 2
      return layer

   def filter_data(self, regex='([a-zA-Z]+ \[mm\]|\[rad\]|\(cylinder\)|ai)'):
      """
      Used to filter data col by regex string
      :param regex: regex string to filter
      :return:
      """
      return self.dp.filter(regex=regex)

   @staticmethod
   def get_avg(data):
      """
      Used to get the average
      :param data: income data
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
      Used to add new column(s) into the data
      :param col_name: column name
      :param data: income data
      """
      if isinstance(col_name, list):
         for col in col_name:
            self.dp[str(col)] = data
      else:
         self.dp[str(col_name)] = data

   def run(self):
      """
      Main processing
      :return:
      """
      self.get_avg_delta_uts()
      self.get_avg_variance_delta_uts()
      self.get_avg_zs()
      self.get_avg_variance_zs()
      self.get_avg_co_variance_delta_uts()
      self.get_slops()
      self.get_intercepts()
      self.get_avg_ms()
      self.get_avg_as()
      self.get_R2s()
      self.get_deformations()
      self.get_interface()
      logger.info(self.interface)
      self.deformations[1] = self.interface
      self.deformations.append(self.F)
      self.deformations.append(round(self.time, 3))
      return self.deformations

def main(args):
   """
   Main process
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
