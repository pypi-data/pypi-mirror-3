#!/usr/bin/env python
#coding: utf-8


__created__ = "2009/09/27"
__author__ = "xlty.0512@gmail.com"
__author__ = "牧唐 杭州"

import web

urls = ('/upload', 'Upload')

class Upload:
    def GET(self):
        return """<html><head></head><body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile" />
<br/>
<input type="submit" />
</form>
</body></html>"""

    def POST(self):
        print ">>>>>>>>>>>>>>", web.input()
        x = web.input(myfile={})
        web.debug(x['myfile'].filename) # This is the filename
        web.debug(x['myfile'].value) # This is the file contents
        web.debug(x['myfile'].file.read()) # Or use a file(-like) object
        print "<<<<<<<<<<<<<<<",web.input().x, web.input().ty, ">>>>>>>>>>>>>>>"
        raise web.seeother('/upload')

if __name__ == "__main__":
   app = web.application(urls, globals()) 
   app.run()

