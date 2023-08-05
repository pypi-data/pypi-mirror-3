#!/usr/bin/env python
#coding: utf-8


__created__ = "2009/09/27"
__author__ = "xlty.0512@gmail.com"
__author__ = "牧唐 杭州"

from httplib import HTTPConnection

HTTPConnection.debuglevel=5

from fetcher import *

from unittest import TestCase
import BaseHTTPServer
import SimpleHTTPServer
from threading import Thread
import urllib, urlparse
import logging
from cStringIO import StringIO

class MySimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):

#        print "do post"
        code = typex = leng = text = None
        #根据传入参数code, 解析要返回的response code
        if "Content-Length" in self.headers:
            cl = int(self.headers["Content-Length"])
            ct = self.headers["Content-Type"]
            data = self.rfile.read(cl)
            ps = data
            if "multipart" in ct:
                cts = ct.split("; ")
                cc = []
                for c in cts:
                    if "=" in c:
                        cc.append(c.split("="))
                
                params = dict(cc)
                boundary = params["boundary"]
                
                multis = data.split("--"+boundary)
                for m in multis:
                    if m.endswith("--\r\n"): break
                    print "parsed qs:>>", m
                    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

        text = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>\n
                            <title>Directory listing for</title>\n
                            <body>
                                                                    淘宝\n
                                                                    中测定发生发生的发生的fsd发送方式地方
                                                                我是中文我是中文, 巍峨哦是中
                            <h2>Directory listing for</h2>\n
                            <hr>\n<ul>\n
                            <img src="./a.jpg"/>
                            </body>
                            </html>""".encode("gb2312")

        leng = len(text)

        self.send_response(code or 200)
        self.send_header("r-type", "post")
        self.send_header("Content-type", typex or "text/plain")
        self.send_header("Content-Length", leng or 0)
        self.end_headers()
        self.wfile.write(text)
        self.wfile.close()

def run():
    def run_while_true(server_class=BaseHTTPServer.HTTPServer,
                       handler_class=MySimpleHTTPRequestHandler):
        server_address = ('', 8199)
        httpd = server_class(server_address, handler_class)
        while 1:
#            print "serving"
            httpd.handle_request()
    run_while_true()

t = Thread(target=run)
t.daemon = True
t.start()

"""
-----------------------------41184676334 
Content-Disposition: form-data; name="attachment"; filename="setup.py" 
Content-Type: application/octet-stream 

#!/usr/bin/env python #coding=utf-8 __created__ = "2009/09/27" __author__ = "xlty.0512@gmail.com" __author__ = "牧唐 杭州" from setuptools import setup, find_packages setup( name="fetcher", version="0.9.1", packages=find_packages(), install_requires=['chardet'], # metadata for upload to PyPI author="Mutang(牧唐)", author_email="xlty.0512@gmail.com", description="simple python fetcher, support head, get, post action, file upload, etc", license="New BSD License", keywords="python fetcher spider charset", url="http://code.taobao.org/trac/fetcher", test_suite="tests.fetcher_tests", dependency_links=[ "http://code.taobao.org/svn/fetcher/" ], ) 
-----------------------------41184676334 
Content-Disposition: form-data; name="description" 

this is setup file 
"""

fetcher = Fetcher()
d = fetcher.fetch("http://localhost:8080/upload", {"x":("1", "2"),"ty":["xv",'123'],"xx":"1454", "myfile": 
                                                   ("test.txt", open("./__init__.py", 'rb')),"myfile2": ("test2.txt", open("./__init__.py", 'rb')),})

print d

if __name__ == "__main__":
    import time
    time.sleep(3000)
