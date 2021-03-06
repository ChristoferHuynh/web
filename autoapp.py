# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from web.app import create_app
from web.settings import DevConfig, ProdConfig

#CONFIG = DevConfig if get_debug_flag() else ProdConfig
CONFIG = DevConfig
app = create_app(CONFIG)
