# -*- coding: utf-8 -*-
from collective.dancing.composer import plone_html_strip_not_likey


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
    plone_html_strip_not_likey.extend([{'id': 'content-history'},
                                       {'class': 'documentByLine'},
                                       ])