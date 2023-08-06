# -*- coding: utf-8 -*-
"""
    flaskext.jade2underscore
    ~~~~~~~~~~~~~~~~~~~~~~~~

    A small Flask extension that makes it easy to use Jade and Underscore
    templates (used in Backbone) with your Flask application.

    :copyright: (c) 2012 by Manuel Albarrán.
    :license: MIT, see LICENSE for more details.
"""

import os.path
import codecs

from pyjade.utils import process
from pyjade.ext.underscore import Compiler as UnderscoreCompiler

def _convert(src, dst):
    template = codecs.open(src, 'r', encoding='utf-8').read()
    output = process(template,compiler=UnderscoreCompiler)
    outfile = codecs.open(dst, 'w', encoding='utf-8')
    outfile.write(output)
    outfile.close()

    print 'compiled "%s" into "%s"' % (src, dst)

def jade2underscore(app, underscore_folder='templates', jade_folder='src/jade', force=False):
    if not hasattr(app, 'static_url_path'):
        from warnings import warn
        warn(DeprecationWarning('static_path is called '
                                'static_url_path since Flask 0.7'),
                                stacklevel=2)
        static_url_path = app.static_path
    else:
        static_url_path = app.static_url_path

    def _jade2underscore(filepath):
        jadefile = "%s/%s.jade" % (jade_folder, filepath)
        filename = "%s/%s.tpl" % (underscore_folder, filepath)
        underscorefile = "%s%s/%s" % (app.root_path, static_url_path, filename)

        if os.path.exists(jadefile) and (force or \
           not os.path.exists(underscorefile) or \
           os.path.getmtime(jadefile) > os.path.getmtime(underscorefile)):
            _convert(jadefile, underscorefile)
            
        return app.send_static_file(filename)
        
    app.add_url_rule("%s/%s/<path:filepath>.tpl" %(static_url_path, underscore_folder), 'jade2underscore', _jade2underscore)
