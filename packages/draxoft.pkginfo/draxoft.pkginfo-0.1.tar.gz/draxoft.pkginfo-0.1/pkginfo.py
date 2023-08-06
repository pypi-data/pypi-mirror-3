#!/usr/bin/env python
#-*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys
    from draxoft.tools import _pkginfo
    retcode = _pkginfo.main()
    sys.exit(retcode)
