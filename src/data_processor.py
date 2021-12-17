# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
 Authors: 

 Usage example:
   - <Script>
"""

import logging
import sys
import re
import utility as util

logger = logging.getLogger(__name__)

class DataProcessor(object):
   """docstring for DataProcessor"""

   def __init__(self, *args, **kwargs):
      self.conf = kwargs.get('config', util.get_config())
      super(DataProcessor, self).__init__()
      self.arg = kwargs.get('arg', None)
      self.data = kwargs.get('data', None)

   def split_by_image(self):
      """
      Split data into multiple frames
      :return:
      """
      data_arr = []
      for i in range(int(self.conf.getint('general', 'rectangle_count'))):
         if i == 0:
            i = ''
         else:
            i = '\.%d' % i
         data = self.data.filter(regex='(\[mm\]|\[rad\]|\(cylinder\))%s$'%(
            i))
         data_arr.append(data.rename(columns=lambda x: re.sub(i, '', x)))
      return data_arr

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
