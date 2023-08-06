"""
stripeol.py
"""

import os
import sys
import logging

from tempfile import NamedTemporaryFile
try:
    from tempfile import SpooledTemporaryFile
    def TemporaryFile(**kwargs):
        return SpooledTemporaryFile(max_size=4*1024*1024, **kwargs)
except ImportError:
    from tempfile import TemporaryFile

from detect import istextfile

def stripeol(filename, options=None):
    """ stripeol """
    if options is None:
        # default options
        class options:
            force = False
            dry_run = False
            no_empty_line = False

    if os.path.getsize(filename)==0:
        logging.info("Skipping %s empty file...", filename)
        return
    # detect binary file
    if not options.force and not istextfile(filename):
        logging.info("Skipping %s binary file...", filename)
        return

    changed = False
    prefix = os.path.basename(filename)
    dirname = os.path.dirname(os.path.realpath(filename))
    with NamedTemporaryFile(prefix=os.path.basename(filename), dir=dirname, delete=False) as ftmp:
        with open(filename) as rsrc:
            for line in rsrc:
                line = line.rstrip("\n")
                if options.no_empty_line and line.strip()=="":
                    ftmp.write(line+"\n")
                    continue
                strip_line = line.rstrip()
                if not changed and line != strip_line:
                    changed = True
                ftmp.write(strip_line+"\n")
    if options.dry_run:
        os.unlink(ftmp.name)
    else:
        os.rename(ftmp.name, filename)
    if changed:
        logging.warning("Stripped whitespace from: %s", filename)
