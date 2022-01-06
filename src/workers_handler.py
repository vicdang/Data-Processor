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
   - workers_hander.py <options>

"""
import logging
import queue
import sys
import threading
import time

from data_parser import DataParser
# from data_processor import DataProcessor
from data_processor_v2 import DataProcessor

logger = logging.getLogger(__name__)

class WorkersHandler(object):
   """docstring for WorkersHandler"""

   def __init__(self, *args, **kwargs):
      super(WorkersHandler, self).__init__()
      self.queue = queue.Queue()
      self.arg = kwargs.get('arg', None)
      self.tasks = kwargs.get('tasks', None)
      self.workers = range(kwargs.get('workers', 10) - 1)

   def thread_func(self, q_item, thread_no):
      """
      Sub function for running tasks in parallel
      :param q_item: Queue items
      :param thread_no: Thread identifier
      """
      while True:
         task_item = q_item.get()
         name = next(iter(task_item))
         # dpc = DataProcessor(data=task_item[name])
         dpc = DataProcessor(data=task_item[name])
         logger.info(name)
         dpc.run()
         # time.sleep(1)
         # logger.info(task_item[name])
         # data = dpc.execute_calculate()
         # data = dpc.split_by_frame()
         # n = 0
         # output = "output/img[%s].csv" % (name)
         # DataParser.export_data(data, output)
         # for i in data:
         #    output = "output/img[%s]_R%s.csv" % (name, str(n))
         #    DataParser.export_data(i, output)
         #    n += 1
         q_item.task_done()
         logger.debug('Thread [%s] is doing task [%s]...' % (str(thread_no),
                                                             str(name)))

   def start_workers(self):
      """
      Using to start workers
      """
      for worker in self.workers:
         wk = threading.Thread(target=self.thread_func,
                               args=(self.queue, worker,),
                               daemon=True)
         wk.start()

   def start_tasks(self, version=1):
      """
      Using to start tasks
      """
      if version == 1:
         for k, v in self.tasks.items():
            self.queue.put({k: v})
      elif version == 2:
         for k, v in self.tasks.items():
            for i in range(int(k.split(':')[0])):
               self.queue.put({'%s:%s' % (k, i): v.loc[i]})
      self.queue.join()

   def run(self):
      """
      Executor
      """
      self.start_workers()
      self.start_tasks(self.arg.app_version)

def main(args):
   """
   Main processing
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
