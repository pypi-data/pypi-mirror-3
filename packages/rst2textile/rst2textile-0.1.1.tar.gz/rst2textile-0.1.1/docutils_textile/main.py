#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
docutils textile.

:copyright: Copyright 2012 by Takayuki SHIMIZUKAWA.
:license: Apache Software License
"""

__docformat__ = 'reStructuredText'

import docutils.core

description = """`rst2textile` is docutils textile writer convert reStructuredText(rst) to Textile format."""


def main():
    output = docutils.core.publish_cmdline(
            writer_name='docutils_textile',
            usage='usage',
            description=description,
            )
    return 0

if __name__ == '__main__':
    main()
