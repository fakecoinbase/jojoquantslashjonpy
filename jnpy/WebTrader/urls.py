#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/3/9 下午9:10
@Author   :   Fangyang
"""
from jnpy.WebTrader.apps.login.urls import login_urls_tuple
from jnpy.WebTrader.apps.dataloader.urls import dataloader_urls_tuple
from jnpy.WebTrader.apps.backtester.urls import backtester_urls_tuple

URL_TUPLE_List = []
URL_TUPLE_List += login_urls_tuple
URL_TUPLE_List += dataloader_urls_tuple
URL_TUPLE_List += backtester_urls_tuple


if __name__ == "__main__":
    pass
