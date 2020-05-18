from pathlib import Path

from vnpy.trader.app import BaseApp

from .engine import BacktesterEngineJnpy, APP_NAME


class CtaBacktesterJnpyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA回测"
    engine_class = BacktesterEngineJnpy
    widget_name = "JnpyBacktesterManager"
    icon_name = "Meowth.svg"
