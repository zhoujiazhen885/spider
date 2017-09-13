#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

测试爬虫代码

"""

import urllib2
import re

#定义download函数

def download(url, user_agent='jiazhen', num_retries=2):
    print 'Downloading:', url
    headers = {'User-agent':user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries >0:
            if hasattr(e,'code') and 500 <= e.code <600:
                # retry 5xx HTTP errors
                return download(url, user_agent, num_retries-1)
    print html
    return html

def crawl_sitemap(url):
    # download the sitemap file
    sitemap = download(url)
    # extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = download(link)
        # scrape html here

if __name__ == '__main__':
    crawl_sitemap('http://example.webscraping.com/sitemap.xml')
   # crawl_sitemap('http://www.baidu.com')
