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
REV_BEFORE = 0
REV_AFTER = 0
GROUP = 0

class WorkersHandler(object):
   """docstring for WorkersHandler"""

   def __init__(self, **kwargs):
      super(WorkersHandler, self).__init__()
      global REV_BEFORE
      global REV_AFTER
      global GROUP
      self.conf = kwargs.get('config', util.get_config())
      self.arg = kwargs.get('arg', None)
      self.tasks = kwargs.get('tasks', None)
      self.debug = self.conf.getboolean("app", "debug")
      self.verbose = self.conf.getboolean("app", "verbose")
      self.groups = GROUP = self.conf.getint("app", "group_by")
      self.workers = range(self.conf.getint("app", "workers"))
      self.rev_before = REV_BEFORE = self.conf.getint("app", "reserve_before")
      self.rev_after = REV_AFTER = self.conf.getint("app", "reserve_after")
      self.deformations = {}
      self.dt = None
      self.results = {}

   def thread_func(self, q_item, thread_no, analysis=False):
      """
      Sub function for running tasks in parallel
      :param q_item: Queue items
      :param thread_no: Thread identifier
      :param analysis: Analysis mode on or off
      """
      while True:
         task_item = q_item.get()
         if not analysis:
            name = next(iter(task_item))
            dp = DataProcessor(data=task_item[name],
                               name=int(name.split(':')[-1]))
            dp.run()
            self.deformations.update({int(name.split(':')[-1]): dp.deformations})
         else:
            da = DataAnalysis(data=task_item)
            name, data = da.run()
            self.results.update({name: data})
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
      global REV_BEFORE
      flag = 0
      if analysis:
         for k, v in tasks.items():
            logger.debug("k : %s - v : %s" % (k, v))
            q.put({k: v})
      else:
         for k, v in tasks.items():
            count = k.split(':')[1].split('-')
            n, m = 0, 1
            for i in range(int(count[0]), int(count[1])):
               gap = n * GROUP + REV_BEFORE
               if i >= gap:
                  if i == (n + 1) * GROUP:
                     n += 1
                     continue
                  else:
                     q.put({'%s:%s' % (k, i): v.loc[i]})
      q.join()

   def run_pre_calculation(self):
      """
      Run Pre calculation
      """
      q = queue.Queue()
      self.start_workers(self.thread_func, q)
      self.start_tasks(q, self.tasks, analysis=False)
      if self.verbose:
         logger.debug(json.dumps(self.deformations, indent=3))
      self.dt = util.slice_data(self.deformations,
                                self.groups, rev_before=self.rev_before)
      if self.debug:
         with open("./output/deformation.json", "w") as f:
            f.write(json.dumps(self.deformations, indent=2, sort_keys=True))

   def run_analysis(self):
      """
      Run analysis
      """
      q = queue.Queue()
      self.start_workers(self.thread_func, q, range(len(self.deformations)),
                         analysis=True)
      self.start_tasks(q, self.dt, analysis=True)
      self.export_data()

   def export_data(self):
      """
      Used to export data
      """
      logger.debug(self.results)
      DataParser.export_data(self.results, file_name="final", concat=True,
                             transpose=True)

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
   logger.debug(args)
   return

if __name__ == '__main__':
   main(sys.argv[1:])
