"""
docutils textile.

:copyright: Copyright 2012 by Takayuki SHIMIZUKAWA.
:license: Apache Software License
"""

__docformat__ = 'reStructuredText'

from docutils_textile.writer import TextileWriter as Writer  #for docutils rule.
    #if docutils receive 'foo' as writer name, execute `import foo.Writer`.


# setup hook for sphinx
def setup(app):
    from docutils_textile.builder import SphinxTextileBuilder
    app.add_builder(SphinxTextileBuilder)  #sphinx builder registration
