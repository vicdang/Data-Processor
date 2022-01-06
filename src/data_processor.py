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
      self.d_ut = None
      self.create_ut()
      logger.info(self.d_ut)
      pd.set_option('display.max_columns', None)

   def create_ut(self):
      d = {}
      for i in range(25):
         d.update({'d_ut_R%d' % i: []})
      self.d_ut = pd.DataFrame(d)

   def split_by_frame(self):
      """
      Split data into multiple frames
      :return:
      """
      data_arr = []
      for i in range(int(self.conf.getint('general', 'rectangle_count'))):
         i = '\.%d' % i
         data = self.dp.filter(regex='([a-zA-Z ]+(\[mm\]|\[rad\]|\('
                                       'cylinder\))[\.0-9]+)|d_ut')
         # data = self.data
         # data_arr.append(data.rename(columns=lambda x: re.sub(i, '', x)))
         # data_arr.append(data)
      # return data_arr
      return self.dp

   def execute_calculate(self):
      data = None
      self.exec_ut()
      return data

   def exec_ut(self):
      self.add_col(["avg_d_ut_L0", "avg_d_ut_L2",
                    "avg_var_d_ut_L0", "avg_var_d_ut_L2",
                    "avg_covar_d_ut_L0", "avg_covar_d_ut_L2"])
      for index, row in self.dp.iterrows():
         avg_d_ut = self.get_avg_d_ut(index)
         self.dp.loc[index,
                     ["avg_d_ut_L0",
                      "avg_d_ut_L1",
                      "avg_d_ut_L2"]] = [avg_d_ut[0], avg_d_ut[1], avg_d_ut[2]]
      for index, row in self.dp.iterrows():
         avg_var_d_ut = self.get_avg_var_d_ut(index)
         self.dp.loc[index,
                     ["avg_var_d_ut_L0",
                      "avg_var_d_ut_L1",
                      "avg_var_d_ut_L2"]] = [avg_var_d_ut[0], avg_var_d_ut[1],
                                             avg_var_d_ut[2]]

      for index, row in self.dp.iterrows():
         avg_covar_d_ut = self.get_avg_covar_d_ut(index)
         self.dp.loc[index,
                     ["avg_covar_d_ut_L0",
                      "avg_covar_d_ut_L1",
                      "avg_covar_d_ut_L2"]] = [avg_covar_d_ut[0],
                                               avg_covar_d_ut[1],
                                               avg_covar_d_ut[2]]


   def get_avg_covar_d_ut(self, index):
      covar_d_ut = self.get_covar_d_ut(index)
      return self.get_avg(covar_d_ut)

   def get_covar_d_ut(self, index):
      covar_dut = []
      layer = None
      for i in range(25):
         if i < 12:
            layer = 0
         elif i == 12:
            layer = 1
         else:
            layer = 2
         covar_dut.append(float(self.d_ut.loc[index, ['d_ut_R%d' % i]]) -
                          float(self.dp.loc[index, ['avg_d_ut_L%d' % layer]]) *
                  (float(self.dp.loc[index, ['Z [mm] (cylinder).%d' % (i+1)]]) -
                   float(self.get_avg_z(index)[layer])))
      return [covar_dut[:12], covar_dut[12], covar_dut[12:]]

   def get_avg_var_d_ut(self, index):
      var_d_ut = self.get_var_d_ut(index)
      return self.get_avg(var_d_ut)

   def get_var_d_ut(self, index):
      var_dut = []
      layer = None
      for i in range(25):
         if i < 12:
            layer = 0
         elif i == 12:
            layer = 1
         else:
            layer = 2
         var_dut.append(pow(float(self.d_ut.loc[index, ['d_ut_R%d' % i]]) -
                            float(self.dp.loc[index, ['avg_d_ut_L%d' %
                                                      layer]]), 2))
      return [var_dut[:12], var_dut[12], var_dut[12:]]


   def get_avg_z(self, index, reg_z='^Z \[mm\]\.[0-9]+$'):
      z = self.get_z(index, self.filter_data(index, reg_z))
      return self.get_avg(z)

   def get_z(self, index, data):
      z = []
      for d in data:
         z.append(float(d))
      return [z[:12], z[12], z[12:]]

   def get_avg_d_ut(self, index, reg_r='^R \[mm\]\.[0-9]+$',
                    reg_d_theta='^dTheta \[rad\]\.[0-9]+$'):
      d_ut = self.get_d_ut(index, self.filter_data(index, reg_r),
                           self.filter_data(index, reg_d_theta))
      return self.get_avg(d_ut)

   def get_d_ut(self, index, r_mm, d_theta):
      i = 0
      dut = []
      d = {}
      for r in r_mm:
         if i == 0:
            v = r * d_theta[i]
         else:
            v = (r * d_theta[i]) - dut[0]
         # d.update({'d_ut_R%d' % i : [v]})
         self.d_ut.loc[index, ['d_ut_R%d' % i]] = v
         dut.append(v)
         i += 1
      # self.d_ut.append(d)
      return [dut[:12], dut[12], dut[12:]]

   def filter_data(self, index,
                   regex='([a-zA-Z]+ \[mm\]|\[rad\]|\(cylinder\))'):
      return self.dp.iloc[index].filter(regex=regex)

   def generate_delta(self, data):
      pass

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
      """
      Executor
      :return:
      """
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
