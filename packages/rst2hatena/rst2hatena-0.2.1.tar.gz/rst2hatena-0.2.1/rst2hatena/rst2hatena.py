#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
A minimal front end to the Docutils Publisher, producing Hatena.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description

import hatena_writer

description = ('Generates Hatena documents from standalone reStructuredText '
               'sources.  ' + default_description)


def main():
    publish_cmdline(writer=hatena_writer.Writer(), description=description)

if __name__ == '__main__':
    main()
