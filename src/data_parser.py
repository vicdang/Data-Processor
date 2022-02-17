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
   - data_parser.py <options>

"""
import logging
import sys

import pandas as pd
import utility as util

logger = logging.getLogger(__name__)

class DataParser(object):
   """docstring for DataParser"""

   def __init__(self, *args, **kwargs):
      super(DataParser, self).__init__()
      self.arg = kwargs.get('arg', None)
      self.conf = kwargs.get('config', util.get_config())
      self.data = None
      self.file_01 = self.arg.file_01
      self.file_02 = self.arg.file_02
      self.output_file = self.arg.output_file
      self.records_count = 0
      self.sliced_data = {}
      self.rev_before = self.conf.getint("general", "reserve_before")
      self.rev_after = self.conf.getint("general", "reserve_after")
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
   def export_data(data, file_name=None, concat=False, transpose=False,
                   **kwargs):
      """
      Using to export the data into file
      :param transpose:
      :param concat:
      :param data: Data in
      :param file_name: Output file
      """
      if file_name:
         file_name += "_"
      f_n = './output/%s%s.csv' % (file_name, 'result')
      if type(data) in [dict]:
         if concat:
            res = pd.concat(data,
                            axis=1,
                            join="inner",
                            ignore_index=kwargs.get('ignore_index', True),
                            keys=None,
                            levels=1,
                            names=None,
                            verify_integrity=False,
                            copy=True,
                            sort=True,)
            if transpose:
               res = res.transpose()
            logger.debug("Exporting: %s" % f_n)
            res.to_csv(f_n, index=False, header=True, encoding='utf-8')
         else:
            for k, v in data.items():
               f_n = '%s/result_%s.csv' % (file_name, k)
               logger.debug("Exporting: %s" % f_n)
               v.transpose().to_csv(f_n,
                                    index=True,
                                    header=True,
                                    encoding='utf-8')
      else:
         logger.debug("Exporting: %s" % f_n)
         data.to_csv(f_n, index=True, header=True, encoding='utf-8')


   def slice_data(self, analysis=False):
      """
      Using for slicing the data into multipe record-groups
      :param analysis: analysis on for off
      """
      records_count = self.records_count - self.rev_before - self.rev_after
      step = int(self.arg.group_count)
      groups = int(records_count / step) + 1
      data = None
      logger.debug("Total rows: %d - Selected: %d - Slice: %d - Groups: %d" % (
                   self.records_count, records_count, step, groups))

      if analysis:
         for item in range(0, groups):
            if item > 0:
               i = step * item
            else:
               i = (step * item) + self.rev_before
            j = i + step - 1
            data = {"%s:%s-%s" % (records_count,
                                  i, j): self.data.loc[i:j, :]}
      else:
         i = self.rev_before
         j = self.records_count - self.rev_after
         data = {"%s:%s-%s" % (records_count, i, j):
                 self.data.loc[i:j, :]}
      if self.arg.verbose:
         logger.debug(data)
      self.sliced_data.update(data)

   def run(self):
      """
      Executor
      """
      data_01 = self.read_data(self.file_01, sep=',', index_col="Count",
                               header=0)
      data_02 = self.read_data(self.file_02, sep=',', index_col="Index [1]",
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
