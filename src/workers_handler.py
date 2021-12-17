# -*- coding: utf-8 -*-
# vim:ts=3:sw=3:expandtab
"""
 Authors: 

 Usage example:
   - <Script>
"""
import logging
import queue
import sys
import threading

from data_parser import DataParser
from data_processor import  DataProcessor

logger = logging.getLogger(__name__)

class WorkersHandler(object):
   """docstring for WorkersHandler"""

   def __init__(self, *args, **kwargs):
      super(WorkersHandler, self).__init__()
      self.queue = queue.Queue()
      self.arg = kwargs.get('arg', None)
      self.tasks = kwargs.get('tasks', None)
      self.workers = range(kwargs.get('workers', 10) - 1)

   @staticmethod
   def func(q_item, thread_no):
      """
      Sub function for running tasks in parallel
      :param q_item: Queue items
      :param thread_no: Thread identifier
      """
      while True:
         task_item = q_item.get()
         name = next(iter(task_item))
         dpc = DataProcessor(data=task_item[name])
         data = dpc.split_by_image()
         n = 0
         for i in data:
            output = "output/range[%s]_img[%s].csv" % (name, str(n))
            DataParser.export_data(i, output)
            n += 1
         q_item.task_done()
         logger.debug('Thread [%s] is doing task [%s]...' % (str(thread_no),
                                                             str(name)))

   def start_workers(self):
      """
      Using to start workers
      """
      for worker in self.workers:
         wk = threading.Thread(target=self.func,
                               args=(self.queue, worker,),
                               daemon=True)
         wk.start()

   def start_tasks(self):
      """
      Using to start tasks
      """
      for k, v in self.tasks.items():
         self.queue.put({k: v})
      self.queue.join()

   def run(self):
      """
      Executor
      """
      self.start_workers()
      self.start_tasks()

def main(args):
   """
   Main processing
   :param args:
   :return:
   """
   return

if __name__ == '__main__':
   main(sys.argv[1:])
