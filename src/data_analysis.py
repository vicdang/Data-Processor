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
   - data_analysis.py <options>

"""
import json
import logging
import math
import sys

import numpy as np
import pandas as pd

import utility as util

logger = logging.getLogger(__name__)

class DataAnalysis(object):
   """docstring for DataAnalysis"""

   def __init__(self, *args, **kwargs):
      self.conf = kwargs.get('config', util.get_config())
      super(DataAnalysis, self).__init__()
      self.arg = kwargs.get('arg', None)
      self.data = kwargs.get('data', None)
      self.dp = None
      self.group = None
      self.f = self.conf.getint("analysis", "f")
      self.rext = self.conf.getfloat("analysis", "Rext")
      self.rint = self.conf.getfloat("analysis", "Rint")
      self.delay = self.conf.getfloat("analysis", "delay")
      self.omega = 2 * math.pi * float(self.f)
      self.result = {}
      self.final_result = {}

   def get_data(self):
      self.group, self.dp = list(self.data.items())[0]

   def prepare_data(self):
      self.get_data()
      defor_L0 = []
      defor_L1 = []
      defor_L2 = []
      defor_F = []
      times = []
      for _, modal in self.dp.items():
         defor_L0.append(modal[0])
         defor_L1.append(modal[1])
         defor_L2.append(modal[2])
         defor_F.append(modal[3])
         times.append(modal[4])
      return defor_L0, defor_L1, defor_L2, defor_F, times

   def cal(self, k, modales, times):
      avg_time = np.average(times)
      moyenne = np.average(modales)
      x_arr = []
      xsin = []
      xcos = []
      sin2 = []
      cos2 = []
      sincos = []
      i = 0
      for modal in modales:
         x = modal - moyenne
         mt = self.omega * times[i]
         sin_mt = math.sin(mt)
         cos_mt = math.cos(mt)
         x_arr.append(x)
         xsin.append(x * sin_mt)
         xcos.append(x * cos_mt)
         sin2.append(pow(sin_mt, 2))
         cos2.append(pow(cos_mt, 2))
         sincos.append(sin_mt * cos_mt)
         i += 1
      Xsin = sum(xsin)
      Xcos = sum(xcos)
      Sin2 = sum(sin2)
      Cos2 = sum(cos2)
      SinCos = sum(sincos)
      A = (Xsin * Cos2 - Xcos * SinCos) / (Sin2 * Cos2 - pow(SinCos, 2))
      B = (Xcos * Sin2 - Xsin * SinCos) / (Sin2 * Cos2 - pow(SinCos, 2))
      x0 = math.sqrt(pow(A, 2) + pow(B, 2))
      phi = math.atan(B / A) * 180 / math.pi
      approached_signal_1 = []
      approached_signal_2 = []
      for t in times:
         mt = self.omega * t
         sin_mt = math.sin(mt)
         cos_mt = math.cos(mt)
         approached_signal_1.append((A * cos_mt) + (B * sin_mt))
         approached_signal_2.append((A * sin_mt) + (B * cos_mt))

      quality_1 = []
      quality_2 = []
      i = 0
      for x in x_arr:
         quality_1.append(abs(approached_signal_1[i] - x) / x0)
         quality_2.append(abs(approached_signal_2[i] - x) / x0)
         i += 1
      Quality = min(np.average(quality_1), np.average(quality_2)) * 100

      return {"Amplitude": x0, "phi": phi, "Quality (%)": Quality}

   def cal_data(self, data):
      key = ["L0", "L1", "L2", "F"]
      for k in key:
         self.result.update({k: self.cal(k, data[key.index(k)], data[-1])})
      self.result.update({'time': np.average(data[-1])})

   def cal_pressure(self):
      x0_pressure = (3 * self.result['F']['Amplitude']) / (2 * math.pi * (
            self.rext**3 - self.rint**3)) / 10**6
      self.result.update({'P': {'Amplitude': x0_pressure}})
      try:
         G_L0 = x0_pressure / self.result['L0']['Amplitude'] * 10**6
      except ZeroDivisionError:
         G_L0 = 0
      try:
         K_L1 = x0_pressure / self.result['L1']['Amplitude'] * 10**6
      except ZeroDivisionError:
         K_L1 = 0
      try:
         G_L2 = x0_pressure / self.result['L2']['Amplitude'] * 10**6
      except ZeroDivisionError:
         G_L2 = 0
      phi_F = self.result['F']['phi']
      phi_G0 = phi_F - self.result['L0']['phi']
      if phi_G0 < 0:
         phi_G0 += 180
      phi_G0 -= self.delay
      phi_K1 = phi_F - self.result['L1']['phi']
      if phi_K1 < 0:
         phi_K1 += 180
      phi_K1 -= self.delay
      phi_G2 = phi_F - self.result['L2']['phi']
      if phi_G2 < 0:
         phi_G2 += 180
      phi_G2 -= self.delay
      self.result.update({'G_L0': {'G0': G_L0,
                                   'phi_G0': phi_G0},
                          'K_L1': {'K1': K_L1,
                                   'phi_K1': phi_K1},
                          'G_L2': {'G2': G_L2,
                                   'phi_G2': phi_G2}})

   def run(self):
      """
      Main processing
      :return:
      """
      data = self.prepare_data()
      self.cal_data(data)
      self.cal_pressure()
      self.final_result.update({self.group: self.result})
      logger.debug(json.dumps(self.final_result, indent=3))
      res = pd.DataFrame.from_dict(self.final_result)
      # res = pd.DataFrame(dict([(col_name,
      #                           pd.Series(values)) for col_name, values in
      #                           self.final_result.items()]))
      return self.group, res

def main(args):
   """
   Main process
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
