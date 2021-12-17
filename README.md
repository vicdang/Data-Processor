# Data Processor
Using to generate and process data
## Prerequisites
- Python >= 3.8
- Pandas
- Numpy

## Structure
Directory structure is shown below:

```
\.
|---main.py
|---README.md
|---requirements.txt
|---run.bat
+---input
|   |---E1.csv
|   \---ExpE.csv
|
\---output
    \---*.csv

```
## Steps
### Install python
 - Install python >= 3.8

### Install required packages
 - pip3 install -r requirements.txt

### Execute command
```
# For quick start
Execute "run.bat", default group 150 items, and uses 10 workers. 

# For general help
$ python main.py -h
usage: main.py [-h] [-d] [-v] {exec} ...

 - Authors: Vic Dang
 - Skype: traxanh_dl
 - Usage example:
   + python main.py -d -v exec -g 100 -w 5

positional arguments:
  {exec}         Subcommand help
    exec         Full Execution

optional arguments:
  -h, --help     show this help message and exit
  -d, --debug
  -v, --verbose

# For sub command help
python main.py <action> -h

$ python main.py exec -h
usage: main.py exec [-h] [-f1 FILE_01] [-f2 FILE_02] [-o OUTPUT_FILE]
                       [-w WORKER_NUM] [-g GROUP_COUNT]

optional arguments:
  -h, --help            show this help message and exit
  -f1 FILE_01, --file-01 FILE_01
                        Path to the first CSV file (default: input/E1.csv)
  -f2 FILE_02, --file-02 FILE_02
                        Path to the second CSV file (default: input/ExpE.csv)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output file name, should be in CSV format. (default:
                        None)
  -w WORKER_NUM, --worker-num WORKER_NUM
                        Workers quantity. (default: 5)
  -g GROUP_COUNT, --group-count GROUP_COUNT
                        Group records by index (default: 150)

# Default execution
python main.py exec

# Enable debug level and verbose
python main.py -d exec
python main.py -d -v exec

# Some others usecases
python main.py -d -v exec \
                  -f1 ".\input\E1.csv" \
                  -f2 ".\input\ExpE.csv" \ 
                  -o ".\output\final.csv" \ 
                  -w 10 \
                  -g 150
```
