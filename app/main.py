from crawler import Crawler
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import jsonmodule as jm

if __name__ == "__main__":
    crawler = Crawler()
    crawler.open()
    input("if you want to finish enter anything")
    crawler.close()