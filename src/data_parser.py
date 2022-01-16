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
   - data_parser.py <options>

"""
import logging
import sys

import pandas as pd

logger = logging.getLogger(__name__)

class DataParser(object):
   """docstring for DataParser"""

   def __init__(self, *args, **kwargs):
      super(DataParser, self).__init__()
      self.arg = kwargs.get('arg', None)
      self.data = None
      self.file_01 = self.arg.file_01
      self.file_02 = self.arg.file_02
      self.output_file = self.arg.output_file
      self.records_count = 0
      self.sliced_data = {}
      pd.set_option('display.max_columns', None)

   @staticmethod
   def read_data(*argv, **kwargs):
      """
      Using to read data from CSV
      :param argv:
      :param kwargs:
      :return: data in Dataframe
      """
      return pd.read_csv(*argv, **kwargs)

   def join_data(self, list_data: list):
      """
      Using to join multiple dataframes
      :param list_data: List of dataframes
      :return:
      """
      self.data = pd.concat(list_data, axis=1)
      self.records_count = int(self.data.shape[0])

   @staticmethod
   def export_data(data, file_name):
      """
      Using to export the data into file
      :param data: Data in
      :param file_name: Output file
      """
      if type(data) in [list]:
         res = pd.concat(data,
                         axis=1,
                         join="outer",
                         ignore_index=False,
                         keys=None,
                         levels=3,
                         names=None,
                         verify_integrity=False,
                         copy=True,
                         sort=True,).transpose()
      else:
         res = data
      logger.debug("Exporting: %s" % file_name)
      res.to_csv(file_name, index=True, header=True, encoding='utf-8')

   def slice_data(self, analysis=False):
      """
      Using for slicing the data into multipe record-groups
      :param analysis: analysis on for off
      """
      step = int(self.arg.group_count)
      groups = int(self.records_count / step) + 1
      data = None
      logger.debug("Total rows: %d - Slice: %d - Groups: %d" % (
         self.records_count, step, groups))

      if analysis:
         for item in range(0, groups):
            i = step * item
            j = i + step - 1
            data = {"%s:%s-%s" % (self.records_count,
                                  i, j): self.data.loc[i:j, :]}
      else:
         data = {"%s:%s-%s" % (self.records_count,
                               0, self.records_count): self.data}
      if self.arg.verbose:
         logger.debug(data)
      self.sliced_data.update(data)

   def run(self):
      """
      Executor
      """
      data_01 = self.read_data(self.file_01, sep=',', index_col="Count",
                               header=0)
      data_02 = self.read_data(self.file_02, sep=';', index_col="Index [1]",
                               header=1)
      self.join_data([data_01, data_02])
      self.slice_data()

def main(args):
   """
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
