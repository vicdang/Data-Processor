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
   - data_analysis.py <options>

"""
import json
import logging
import math
import sys

import numpy as np
import pandas as pd

import utility as util
from data_parser import DataParser

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
      self.sub_result = {}
      self.final_result = {}

   def get_data(self):
      """
      Used to get data
      """
      self.group, self.dp = list(self.data.items())[0]

   def prepare_data(self):
      """
      Used to prepare data
      """
      self.get_data()
      defor_l0 = []
      defor_l1 = []
      defor_l2 = []
      defor_f = []
      times = []
      for _, modal in self.dp.items():
         defor_l0.append(modal[0])
         defor_l1.append(modal[1])
         defor_l2.append(modal[2])
         defor_f.append(modal[3])
         times.append(modal[4])
      return defor_l0, defor_l1, defor_l2, defor_f, times

   def calculation(self, k, modales, times):
      """
      Used to calculate
      :param modales: data of modales
      :param times: times
      :return:
      """
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
      x_sin = sum(xsin)
      x_cos = sum(xcos)
      sin_2 = sum(sin2)
      cos_2 = sum(cos2)
      sin_cos = sum(sincos)
      a = (x_sin * cos_2 - x_cos * sin_cos) / (sin_2 * cos_2 - pow(sin_cos, 2))
      b = (x_cos * sin_2 - x_sin * sin_cos) / (sin_2 * cos_2 - pow(sin_cos, 2))
      x0 = math.sqrt(pow(a, 2) + pow(b, 2))
      phi = math.atan(b / a) * 180 / math.pi
      approached_signal_1 = []
      approached_signal_2 = []
      for t in times:
         mt = self.omega * t
         sin_mt = math.sin(mt)
         cos_mt = math.cos(mt)
         approached_signal_1.append((a * cos_mt) + (b * sin_mt))
         approached_signal_2.append((a * sin_mt) + (b * cos_mt))

      quality_1 = []
      quality_2 = []
      i = 0
      for x in x_arr:
         quality_1.append(abs(approached_signal_1[i] - x) / x0)
         quality_2.append(abs(approached_signal_2[i] - x) / x0)
         i += 1
      quality_fin = min(np.average(quality_1), np.average(quality_2)) * 100

      sub_result = {'Image': self.remake(),
                    'Time': times,
                    '%s_x' % k: x_arr,
                    '%s_signal_1' % k: approached_signal_1,
                    '%s_signal_2' % k: approached_signal_2,
                    '%s_quality_1' % k: quality_1,
                    '%s_quality_2' % k: quality_2}
      main_result = {"%s" % k: x0,
                     "%s_Phi" % k: phi,
                     "%s_Quality" % k: quality_fin}

      return main_result, sub_result

   def remake(self):
      """
      Remake the index of group
      :return:
      """
      gr = self.group.split("-")
      return [i for i in range(int(gr[0]), int(gr[1]) + 1)]

   def cal_data(self, data):
      """
      Used to calculate data in
      :param data: data in
      """
      key = ["Ezz_bas", "Delta_uz", "Ezz_haut", "Charge"]
      self.result.update({'ATime': np.average(data[-1])})
      self.result.update({'AGroup': self.group})
      for k in key:
         main_result, sub_result = self.calculation(k,
                                                    data[key.index(k)],
                                                    data[-1])
         self.result.update(main_result)
         self.sub_result.update(sub_result)

   def cal_pressure(self):
      """
      Used to calculate the pressure
      """
      x0_pressure = (3 * self.result['Charge']) / (2 * math.pi * (
            self.rext**3 - self.rint**3)) / 10**6
      self.result.update({'P': x0_pressure})
      try:
         g_l0 = x0_pressure / self.result['Ezz_bas'] * 10**6
      except ZeroDivisionError:
         g_l0 = 0
      try:
         k_l1 = x0_pressure / self.result['Delta_uz']
      except ZeroDivisionError:
         k_l1 = 0
      try:
         g_l2 = x0_pressure / self.result['Ezz_haut'] * 10**6
      except ZeroDivisionError:
         g_l2 = 0
      phi_f = self.result['Charge_Phi']
      phi_g0 = phi_f - self.result['Ezz_bas_Phi']
      if phi_g0 < 0:
         phi_g0 += 180
      phi_g0 -= self.delay
      phi_k1 = phi_f - self.result['Delta_uz_Phi']
      if phi_k1 < 0:
         phi_k1 += 180
      phi_k1 -= self.delay
      phi_g2 = phi_f - self.result['Ezz_haut_Phi']
      if phi_g2 < 0:
         phi_g2 += 180
      phi_g2 -= self.delay
      self.result.update({'G0': g_l0, 'G0_Phi': phi_g0,
                          'K1': k_l1, 'K1_Phi': phi_k1,
                          'G2': g_l2, 'G2_Phi': phi_g2})

   def export_data(self, data):
      """
      Used to export data
      """
      DataParser.export_data(data, file_name=self.group, concat=False,
                             transpose=True)

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
      res = pd.DataFrame.from_dict(self.final_result, orient='columns')
      sub = pd.DataFrame.from_dict(self.sub_result, orient='columns')
      self.export_data(sub)
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
