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
   - python main.py -d -v exec -g 100 -w 5

"""

import argparse
import logging
import pathlib
import sys
import time
from argparse import ArgumentDefaultsHelpFormatter as Formatter

sys.path.insert(0, './src/')
from src import utility as util
from src.data_parser import DataParser
from src.workers_handler import WorkersHandler

logger = logging.getLogger()
CUR_PATH = pathlib.Path().resolve()

def setup_logging(debug: bool = False):
   """
   Using to setup the logging configuration
   :param debug: Debug flag
   """
   if debug:
      log_level = logging.DEBUG
   else:
      log_level = logging.INFO
   logging.basicConfig(level=log_level,
                       format='%(asctime)s - %(levelname)s %(threadName)s - %('
                              'name)s %(funcName)s %(lineno)d : %('
                              'message)s',
                       stream=sys.stderr,
                       filemode='w')
   global logger
   logger = logging.getLogger('sLogger')

def add_args(parser, action='exec'):
   """
   Using to add args
   :param parser: The main args parser
   :param action: The main action
   """
   if action in ['exec']:
      parser.add_argument('-f1', '--file-01',
                          default='input/E1.csv',
                          help='Path to the first CSV file')
      parser.add_argument('-f2', '--file-02',
                          default='input/ExpE.csv',
                          help='Path to the second CSV file')
      parser.add_argument('-o', '--output-file',
                          # default='output/final.csv',
                          help='Output file name, should be in CSV format.')
      parser.add_argument('-w', '--worker-num',
                          default=5,
                          type=int,
                          help='Workers quantity.')
      parser.add_argument('-g', '--group-count',
                          default=150,
                          type=int,
                          help='Group records by index')

def parse_cli():
   """
   Using to parse the CLI args
   :return: The main arg object
   """
   parser = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument('-d', '--debug', action='store_true')
   parser.add_argument('-v', '--verbose', action='store_true')
   parser.add_argument('-t', '--test', action='store_true',
                       help='Enable test mode')

   subparsers = parser.add_subparsers(help='Subcommand help', dest='action')
   add_args(subparsers.add_parser('exec', formatter_class=Formatter,
                                  help='Full Execution'), 'exec')
   return parser.parse_args()

def main(argv):
   """
   Main process
   :param argv: ARGS from CLI
   :return: Return code
   """
   conf = util.get_config()
   dp = DataParser(arg=argv, config=conf)
   dp.run()
   tasks = dp.sliced_data
   slave = WorkersHandler(arg=argv, tasks=tasks, workers=argv.worker_num,
                          groups=argv.group_count)
   slave.run()
   return

if __name__ == "__main__":
   args = parse_cli()
   setup_logging(args.debug)
   logging.debug('Execute with arguments : %s' % str(args))
   start = time.time()
   main(args)
   end = time.time()
   logger.info("Processed in [" + str(end - start) + "] seconds...")
   # try:
   #    start = time.time()
   #    main(args)
   #    end = time.time()
   #    logger.info("Processed in [" + str(end - start) + "] seconds...")
   # except Exception as err:
   #    logging.error('Performing action: %s' % args.action)
   #    logging.error('ERROR: %s' % err)
