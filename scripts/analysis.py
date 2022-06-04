#!/usr/bin/python3

'''
CLS-SSD Analysis part

Support OS : Linux

우선 소스코드에 있는 코드들을 xml로 만든 후( Using ExtractAndRename ),
해당 파일의 코드들의 simhash를 DBSCAN으로 그룹지어 cluster를 만든 후
각 cluster 중 대표를 xml 파일로 출력한다.

Execution
  python3 ./scripts/analysis.py c function 123 group /path/to/source /path/to/output

argv
  1 - language          = default c ( @TODO py, java, cs ... )
  2 - granularity       = default funtion ( @TODO block )
  3 - clone_type        = default 123 ( @TODO 1|2|3 )
  4 - clone_grouping    = default group ( @TODO pair )
  5 - source_path       = absolute path to source folder
  6 - output_path       = absolute path to output folder
'''

import os
import sys
import time
import collections
import re
import hashlib
import itertools

from bs4 import BeautifulSoup as bf
from Crypto.Util.number import bytes_to_long

class CodeFragment:
  IndexBuilder = {}
  PrimaryKey = itertools.count()
  def __init__(self,file,endline,startline,content):
    self.file = file
    self.startline = startline
    self.endline = endline
    self.content = content
    self.id = next(CodeFragment.PrimaryKey)
    self.tokenizer()
    self.getSimHash()
  
  def tokenizer(self):
    seperator = "[ \t\n\r\f.]"
    self.tokenList = re.split(seperator,self.content)
    self.tokenList = list(filter(lambda x: x != '', self.tokenList))
    self.tokenFrequencyDict = collections.Counter(self.tokenList)

  def getSimHash(self):
    v = [0 for i in range(64)]
    # print(self.tokenFrequencyDict.items())
    for token, frequency in self.tokenFrequencyDict.items():
      hash = bytes_to_long(hashlib.sha256(token.encode()).digest()[:8]) # 64 bit hash in int  TO DO: implement efficient hash
      for i in range(64):
        bit = (hash>>i) & 1
        if bit:
          v[i] += frequency
        else:
          v[i] -= frequency

    self.simhash = 0
    lineCount = self.content.count("\n")
    for freqSum in v:
      if freqSum > 0:
        self.simhash = (self.simhash << 1) | 1
      else:
        self.simhash = (self.simhash << 1) | 0

    log.log("[CodeFragment] binary hash  : %s", format(hash, '#066b'))
    log.log("[CodeFragment] self.simhash : %s", format(self.simhash, '#066b'))

    if lineCount in self.IndexBuilder.keys():
      self.IndexBuilder[lineCount].add(self)
    else:
      self.IndexBuilder[lineCount] = set()
      self.IndexBuilder[lineCount].add(self)

class ICloneIndex:
  def __init__(self, output_path, rename):
    Npath = os.path.join(output_path, f"functions-{rename}.xml")
    CodeFragment.IndexBuilder = dict()
    self.extractFragments(Npath)
    self.extractedFragments = CodeFragment.IndexBuilder
  
  def extractFragments(self, XMLfile):
    '''
    XMLfile : functions.xml의 절대 경로

    expected return : 각 소스코드별 simhash가 담긴 객체 set
    '''
    
    with open(XMLfile, 'r') as f:
      soup = bf(f, features="html.parser")

    for source in soup.findAll('source'): 
      _start = source['startline']
      _end = source['endline']
      _file = source['file']
      _content = source.next_sibling.strip()
      CodeFragment(_start, _end, _file, _content)

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class logger(bcolors):

  def __init__(self, flag):
    self.flag = flag
  
  def log(self, format, *args):
    if self.flag:
      print("[log.py]", self.HEADER + self.WARNING, format%args, self.ENDC)
  
  def warn(self, format, *args):
    if self.flag:
      print("[log.py]", self.HEADER + self.FAIL, format%args, self.ENDC)

log = logger(False)
absolute_root_path = ""

def usage():
  print("Execution")
  print("python3 ./scripts/analysis.py c function 123 blind generous /path/to/source /path/to/output")
  print("  ")
  print("argv")
  print("1 - language          = default c ( @TODO py, java, cs ... )")
  print("2 - granularity       = default funtion ( @TODO block )")
  print("3 - clone_type        = default 123 ( @TODO 1|2|3 )")
  print("4 - clone_grouping    = default group ( @TODO pair )")
  print("5 - source_transform  = default generous or blind")
  print("6 - source_path       = absolute path to source folder")
  print("7 - output_path       = absolute path to output folder")

def analysis(source_path, language='c', granularity='function', clone_type='123', clone_grouping='pair', rename='generous'):
  global absolute_root_path
  absolute_analysis_path = os.path.dirname(os.path.abspath(__file__))
  absolute_root_path = os.path.abspath(os.path.join(absolute_analysis_path, ".."))
  print(absolute_root_path)

  # if len(sys.argv) < 7:
  #   usage()
  #   return
  
  # language = sys.argv[1]
  # granularity = sys.argv[2]
  # clone_type = sys.argv[3]
  # clone_grouping = sys.argv[4]
  rename = "consistent" if rename == "generous" else "blind"
  # source_path = sys.argv[6]
  # output_path = sys.argv[7]
  output_path = os.path.abspath(os.path.join(absolute_root_path, "system"))

  log.log("Argument")
  log.log("  language         : %s", language)
  log.log("  granularity      : %s", granularity)
  log.log("  clone_type       : %s", clone_type)
  log.log("  clone_grouping   : %s", clone_grouping)
  log.log("  rename           : %s", rename)
  log.log("  source_path      : %s", source_path)
  log.log("  output_path      : %s", output_path)
  
  # source data extraction
  # Using ExtractAndRename
  #   ./scripts/ExtractAndRename function c blind source_path output_path
  # output
  #   functions-blind.xml | functions.xml in `output_path`
  
  start = time.time()
  # @TODO ExtractAndRename 속도 향상 필요
  res = os.system(f"{absolute_root_path}/scripts/ExtractAndRename {language} {granularity} {rename} {source_path} {output_path}")
  end = time.time()
  print(f"ExtractAndRename Returned : {res}")
  print("time : {}".format(end - start))

  # Parsing CodeFragment And updated Simhash

  CloneIndex = ICloneIndex(output_path=output_path, rename=rename)
  extractedFragments = CloneIndex.extractedFragments # return set
  return extractedFragments


if __name__ == '__main__':
  analysis()