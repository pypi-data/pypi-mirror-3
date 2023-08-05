# -*- coding: utf-8 -*-
"""The tgapp-smallpress package"""
import tg, os
from whoosh.index import create_in

def plugme(app_config, options):
    def init_whoosh(app):
        from smallpress.model.models import WHOOSH_SCHEMA

        index_path = tg.config.get('smallpress_whoosh_index', '/tmp/smallpress_whoosh')
        if not os.path.exists(index_path):
            os.mkdir(index_path)
            ix = create_in(index_path, WHOOSH_SCHEMA)

        return app

    app_config.register_hook('before_config', init_whoosh)
    return dict(appid='smallpress', global_helpers=False)