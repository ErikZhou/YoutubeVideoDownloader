import os
import sys

from scrapy.cmdline import execute

if __name__ == '__main__':

    # execute(["scrapy", "crawl", "download"])
    # execute(["scrapy", "crawl", "download", "-a", "target=https://www.youtube.com/watch?v=O7KaDi_Po-g"])
    execute(["scrapy", "crawl", "download", "-a", "target=https://www.youtube.com/watch?v=O7KaDi_Po-g&list=PU2XZEtXCC8kXzN4RbFcMLFw"])