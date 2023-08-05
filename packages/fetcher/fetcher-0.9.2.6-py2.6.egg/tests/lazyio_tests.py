#!/usr/bin/env python
#coding: utf-8


__created__ = "2009/09/27"
__author__ = "xlty.0512@gmail.com"
__author__ = "牧唐 杭州"

from fetcher import *

from unittest import TestCase
import BaseHTTPServer
import SimpleHTTPServer
from threading import Thread
import urllib, urlparse
import logging
import nose

def test_lazyio():
    from StringIO import StringIO
    lz = LazyIO(("abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi"))
    assert lz.size == 36
    assert lz.read() == "abcdefghi" * 4
    

def test_lazyio_1():
    from StringIO import StringIO
    lz = LazyIO(("abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi"))
    assert lz.read(2) == "ab"
    assert lz.size == 34
    assert lz.read(2) == "cd"
    assert lz.size == 32
    assert lz.read(1) == "e"
    assert lz.read(2) == "fg"
    assert lz.read(3) == "hia"
    assert lz.read() == "bcdefghiabcdefghiabcdefghi"
    assert lz.size == 0

def test_lazyio_2():
    from StringIO import StringIO
    lz = LazyIO(("abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi"))
    assert lz.read(8) == "abcdefgh"
    assert lz.read(2) == "ia"
    _ff = lz.read(5)
    assert _ff == "bcdef"
    assert lz.read(1) == "g"
    assert lz.read(1) == "h"
    assert lz.read(1) == "i"
    assert lz.read(7) == "abcdefg"
    assert lz.read(1) == "h"
    assert lz.read(1) == "i"

def test_lazyio_3():
    from StringIO import StringIO
    lz = LazyIO(("abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi" , "abc", StringIO("def"), "ghi"))
    assert lz.read(6) == "abcdef"
    assert lz.read(2) == "gh"
    assert lz.read(4) == "iabc"
    assert lz.read(1) == "d"
def test_lazyio_4():
    import logging
    logging.basicConfig(level=logging.DEBUG)

    from StringIO import StringIO
    od = open("./__init__.py", "rb")
    body = {"x":("1", "2"),"ty":["xv",'123'],"xx":"1454", "myfile": ("test.txt", od),"myfile2": ("test2.txt", open("./__init__.py", "rb")),}
    f = Fetcher()
    ct, bd = f.encode_multipart_formdata_readable(body)
#    ct2, bd2 = f.encode_multipart_formdata(body)
    
#    print len(bd2), ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>."
    print bd.buffer.len, "fdsafdsfdsfsdfdsfs"
    s = bd.read(8192)
    print bd.len, bd.size,bd.pos, len(s)
    print len(s) == bd.len

if __name__ == "__main__":
    test_lazyio_4()
#    test_lazyio_3()
#    test_lazyio_2()
#    test_lazyio_1()
#    test_lazyio()