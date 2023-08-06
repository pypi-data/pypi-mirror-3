# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt


import grokcore.json


class JSONP(grokcore.json.JSON):
    """Base class for JSONP views in Grok applications."""

    def __call__(self):
        json = super(JSONP, self).__call__()
        callback = self.request.get('callback').encode('ascii')
        return """%s(%s);""" % (callback, json)
