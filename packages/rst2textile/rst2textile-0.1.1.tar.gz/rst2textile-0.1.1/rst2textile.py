#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
rst2textile.

:copyright: Copyright 2012 by Takayuki SHIMIZUKAWA.
:license: Apache License 2.0.
"""

__docformat__ = 'reStructuredText'

if __name__ == '__main__':
    import sys
    from docutils_textile.main import main
    sys.exit(main())
