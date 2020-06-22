#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/5 下午11:55
@Author   :   Fangyang
"""

import tornado.ioloop
from jnpy.WebTrader.urls import URL_TUPLE_List


app = tornado.web.Application(URL_TUPLE_List, debug=True)
app.listen(8888)
tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    pass
