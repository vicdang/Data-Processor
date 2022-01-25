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
import json
import utility as util

from data_parser import DataParser
from data_processor import DataProcessor
from data_analysis import DataAnalysis

logger = logging.getLogger(__name__)

class WorkersHandler(object):
   """docstring for WorkersHandler"""

   def __init__(self, *args, **kwargs):
      super(WorkersHandler, self).__init__()
      self.arg = kwargs.get('arg', None)
      self.tasks = kwargs.get('tasks', None)
      self.groups = kwargs.get('groups', None)
      self.workers = range(kwargs.get('workers', 10))
      self.deformations = {}
      self.dt = None
      self.results = []

   def thread_func(self, q_item, thread_no, analysis=False):
      """
      Sub function for running tasks in parallel
      :param q_item: Queue items
      :param thread_no: Thread identifier
      :param analysis: Analysis mode on or off
      """
      while True:
         task_item = q_item.get()
         name = None
         if not analysis:
            name = next(iter(task_item))
            dp = DataProcessor(data=task_item[name],
                               name=int(name.split(':')[-1]))
            data = dp.run()
            self.deformations.update({int(name.split(':')[-1]): dp.deformations})
         else:
            da = DataAnalysis(data=task_item)
            name, data = da.run()
            self.results.append(data)
         q_item.task_done()
         logger.debug('Thread [%s] is doing [%s]...' % (str(thread_no),
                                                             str(name)))

   def start_workers(self, thread_func, q, workers=None, **kwargs):
      """
      Using to start workers
      :param thread_func: Thread Functions
      :param q: queue
      :param workers: workers
      """
      workers = workers if workers else self.workers
      for worker in workers:
         wk = threading.Thread(target=thread_func,
                               args=(q, worker,
                                     kwargs.get('analysis'), ),
                               daemon=True)
         wk.start()

   @staticmethod
   def start_tasks(q, tasks, analysis=False):
      """
      Using to start tasks
      :param q: Queue
      :param tasks: Tasks
      :param analysis: analysis on or off
      """
      if analysis:
         for k, v in tasks.items():
            q.put({k: v})
      else:
         for k, v in tasks.items():
            for i in range(int(k.split(':')[0])):
               q.put({'%s:%s' % (k, i): v.loc[i]})
      q.join()

   def run_pre_calculation(self):
      """
      Run Pre calculation
      """
      q = queue.Queue()
      self.start_workers(self.thread_func, q)
      self.start_tasks(q, self.tasks, analysis=False)
      self.dt = util.slice_data(self.deformations, self.groups)
      if self.arg.debug:
         with open("./output/deformation.json", "w") as f:
            f.write(json.dumps(self.deformations, indent=2, sort_keys=True))

   def run_analysis(self):
      """
      Run analysis
      """
      q = queue.Queue()
      self.start_workers(self.thread_func, q, range(len(self.deformations)),
      # self.start_workers(self.thread_func, q, range(1),
                         analysis=True)
      self.start_tasks(q, self.dt, analysis=True)
      self.export_data()

   def export_data(self):
      DataParser.export_data(self.results, "./output/%s.csv" % 'result')

   def run(self):
      """
      Executor
      """
      self.run_pre_calculation()
      self.run_analysis()

def main(args):
   """
   Main processing
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
