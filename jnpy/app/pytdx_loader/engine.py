
import time

import pandas as pd
from datetime import datetime

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.object import BarData
from vnpy.trader.utility import get_folder_path

from jnpy.DataSource.pytdx import ExhqAPI, IPsSource, FutureMarketCode, KBarType

APP_NAME = "PytdxLoader"


class PytdxLoaderEngine(BaseEngine):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.file_path: str = ""

        self.symbol: str = ""
        self.exchange: Exchange = Exchange.SSE
        self.interval: Interval = Interval.MINUTE
        self.datetime_head: str = ""
        self.open_head: str = ""
        self.close_head: str = ""
        self.low_head: str = ""
        self.high_head: str = ""
        self.volume_head: str = ""

    def to_bar_data(self, item,
                    symbol: str,
                    exchange: Exchange,
                    interval: Interval,
                    datetime_head: str,
                    open_head: str,
                    high_head: str,
                    low_head: str,
                    close_head: str,
                    volume_head: str,
                    open_interest_head: str
                    ):
        bar = BarData(
            symbol=symbol,
            exchange=exchange,
            datetime=item[datetime_head].to_pydatetime(),
            interval=interval,
            volume=item[volume_head],
            open_interest=item[open_interest_head],
            open_price=item[open_head],
            high_price=item[high_head],
            low_price=item[low_head],
            close_price=item[close_head],
            gateway_name="DB"
        )
        return bar

    def load_by_handle(
            self,
            data,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            datetime_head: str,
            open_head: str,
            high_head: str,
            low_head: str,
            close_head: str,
            volume_head: str,
            open_interest_head: str,
            datetime_format: str,
            progress_bar_dict:dict,
            opt_str: str
    ):
        start_time = time.time()
        if isinstance(data[datetime_head][0], str):
            data[datetime_head] = data[datetime_head].apply(
                lambda x: datetime.strptime(x, datetime_format) if datetime_format else datetime.fromisoformat(x))
        elif isinstance(data[datetime_head][0], pd.Timestamp):
            self.main_engine.write_log("datetime 格式为 pd.Timestamp, 不用处理.")
        else:
            self.main_engine.write_log("未知datetime类型, 请检查")
        self.main_engine.write_log(f'df apply 处理日期时间 cost {time.time() - start_time:.2f}s')

        if opt_str == "to_db":
            start_time = time.time()
            bars = data.apply(
                self.to_bar_data,
                args=(
                    symbol,
                    exchange,
                    interval,
                    datetime_head,
                    open_head,
                    high_head,
                    low_head,
                    close_head,
                    volume_head,
                    open_interest_head
                ),
                axis=1).tolist()
            self.main_engine.write_log(f'df apply 处理bars时间 cost {time.time() - start_time:.2f}s')

            # insert into database
            database_manager.save_bar_data(bars, progress_bar_dict)

        elif opt_str == "to_csv":

            csv_file_dir = get_folder_path("csv_files")
            data.to_csv(f'{csv_file_dir}/{exchange.value}_{symbol}.csv', index=False)

        start = data[datetime_head].iloc[0]
        end = data[datetime_head].iloc[-1]
        count = len(data)

        return start, end, count

    def load(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            datetime_head: str,
            open_head: str,
            high_head: str,
            low_head: str,
            close_head: str,
            volume_head: str,
            open_interest_head: str,
            datetime_format: str,
            progress_bar_dict: dict,
            opt_str: str,
    ):
        """
        load by filename   %m/%d/%Y
        """
        # data = pd.read_csv(file_path)
        ip, port = IPsSource().get_fast_exhq_ip()
        ex_api = ExhqAPI()
        with ex_api.connect(ip, port):
            params_dict = {
                "category": KBarType[interval.name].value,
                "market": FutureMarketCode[exchange.value].value,
                "code": symbol,
            }
            data_df = ex_api.get_all_KBars_df(**params_dict)

            # transform column name to vnpy format
            data_df.rename(
                columns={
                    "datetime": "Datetime",
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "position": "OpenInterest",
                    "trade": "Volume",
                },
                inplace=True
            )

        return self.load_by_handle(
            data_df,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            datetime_head=datetime_head,
            open_head=open_head,
            high_head=high_head,
            low_head=low_head,
            close_head=close_head,
            volume_head=volume_head,
            open_interest_head=open_interest_head,
            datetime_format=datetime_format,
            progress_bar_dict=progress_bar_dict,
            opt_str=opt_str
        )
