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
      self.Rext = self.conf.getfloat("analysis", "Rext")
      self.Rint = self.conf.getfloat("analysis", "Rint")
      self.F_convert = self.conf.getint("analysis", "F_convert")
      self.delay = self.conf.getfloat("analysis", "delay")
      self.omega = 2 * math.pi * float(self.f)
      self.result = {}

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
         defor_F.append(modal[3] * self.F_convert)
         times.append(modal[4])
      return defor_L0, defor_L1, defor_L2, defor_F, times


   def cal(self, modales, time):
      moyenne = np.average(modales)
      x_arr = []
      xsin = []
      xcos = []
      sin2 = []
      cos2 = []
      sincos = []
      mt = self.omega * time
      sin_mt = math.sin(mt)
      cos_mt = math.cos(mt)
      for modal in modales:
         x = modal - moyenne
         x_arr.append(x)
         xsin.append(x * sin_mt)
         xcos.append(x * cos_mt)
         sin2.append(sin_mt**2)
         cos2.append(cos_mt**2)
         sincos.append(sin_mt * cos_mt)
      Xsin = sum(xsin)
      Xcos = sum(xcos)
      Sin2 = sum(sin2)
      Cos2 = sum(cos2)
      SinCos = sum(sincos)
      A = (Xsin * Cos2 - Xcos * SinCos) / (Sin2 * Cos2 - SinCos**2)
      B = (Xcos * Sin2 - Xsin * SinCos) / (Sin2 * Cos2 - SinCos**2)
      x0 = math.sqrt(A**2 + B**2)
      phi = math.atan(B / A) * 180 / math.pi
      approached_signal_1 = A * cos_mt + B * sin_mt
      approached_signal_1 = A * sin_mt + B * cos_mt

      quality_1 = []
      quality_2 = []
      for x in x_arr:
         quality_1.append(abs(approached_signal_1 - x) / x0)
         quality_2.append(abs(approached_signal_1 - x) / x0)
      Quality = min(np.average(quality_1), np.average(quality_2)) * 100

      return {"x0": x0, "phi": phi, "Quality": Quality, "time": time}


   def run(self):
      """
      Main processing
      :return:
      """
      data = self.prepare_data()
      key = ["L0", "L1", "L2", "F"]
      for k in key:
         self.result.update({"k": self.cal(data[key.index(k)],
                                           np.average(data[ -1]))})
      logger.info(self.result)
      return self.result

def main(args):
   """
   Main process
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
