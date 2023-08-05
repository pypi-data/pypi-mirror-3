# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from simplejson import load


class Configuration(dict):
    def __init__(self, conf_fns):
        self.conf_fns = conf_fns
        for conf_fn in self.conf_fns:
            abs_conf_fn = os.path.abspath(conf_fn)
            if os.path.exists(abs_conf_fn):
                with open(abs_conf_fn) as f:
                    self.update(load(f))
