"""
cli.py
======

Commandline interface for stripeol.
"""

__docformat__ = "restructuredtext"

import os
import sys
import logging
from fnmatch import fnmatch
from optparse import OptionParser

from __init__ import __version__
from stripeol import stripeol

ignore_dirs = [
    '.svn', '.git', '.hg', '.bzr', '.cdv', '.pc', 'CVS', 'RCS', '_darcs',
    '_build', 'autom4te.cache',
]
ignore_postfixes = [
    "*~", "*.swp", "*.bak", ".#*", "core.*"
    "*.pyo", "*.pyc", ".class", "*.o", "*.obj", "*.lo", "*.la", "*.a",
    "*.dll", "*.exe", "*.lib", "*.so",
    "*.rej", "*.egg-info", ".DS_Store",
    "*.gz", "*.bz2", "*.xz", "*.rar", "*.zip", "*.tgz", "*.tbz2", "*.tar.gz",
    "*.tar.bz2", "*.arj", "*.txz", "*.tar.xz",
    "*.jpg", "*.bmp", "*.gif", "*.tif", "*.tiff", "*.png",
]

def ignored(filename, options):
    """ Check if the file should be ignored or not """
    for include in options.includes:
        if fnmatch(filename, include):
            return False
    for exclude in options.excludes:
        if fnmatch(filename, exclude):
            return True
    if options.all_types:
        return False
    for postfix in ignore_postfixes:
        if fnmatch(filename, postfix):
            return True
    return False

def stripfile(path, options):
    logging.info("Stripping file '%s'...", path)
    stripeol(path, options)

def scanpath(path, options):
    if not os.path.exists(path):
        logging.warning("File or directory '%s' does not exist...", path)
        return

    if os.path.isfile(path):
        if not ignored(path, options):
            stripfile(path, options)

    if os.path.isdir(path):
        if not options.recursive:
            logging.info("Skipping directory '%s' recursive not specified...", path)
            return

        for root, dirs, filenames in os.walk(path):
            if any(root.endswith(ignore_dir) for ignore_dir in ignore_dirs):
                logging.info("Skipping directory '%s' ignored...", path)
                continue
            for filename in filenames:
                if ignored(filename, options):
                    logging.info("Skipping file '%s' ignored...", path)
                    continue
                stripfile(os.path.join(root, filename), options)

def main():
    """ stripeol cli main entrypoint """
    usage = "Usage: %prog [options] FILES..."
    parser = OptionParser(prog="stripeol", version="%%prog %s" % __version__)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False, help="Verbosity")
    parser.add_option("-a", "--all-types", dest="all_types", action="store_true",
                      default=False, help="All files are stripped. Do not use the default ignored directory like VCS and backup files.")
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                      default=False, help="Don't show any output")
    parser.add_option("-n", "--dry-run", dest="dry_run", action="store_true",
                      default=False, help="Don't change any files")
    parser.add_option("-l", "--log_file", dest="log_file",
                      default=None, help="Log output to file")
    parser.add_option("-e", "--no-empty-line", dest="no_empty_line", action="store_true",
                      default=False, help="Don't strip whitespace from empty lines")
    parser.add_option("-r", "--recursive", dest="recursive", action="store_true",
                      default=False, help="Recursively go through directories")
    parser.add_option("-f", "--force", dest="force", action="store_true",
                      default=False, help="Force stripping of file even if it might be binary")
    parser.add_option("-i", "--include", dest="includes", action="append", default=[],
                      help="Include PATTERN, can be specified multiple times")
    parser.add_option("-x", "--exclude", dest="excludes", action="append", default=[],
                      help="Exclude PATTERN, can be specified multiple times")
    parser.add_option
    (options, args) = parser.parse_args()
    if len(args)<1:
        parser.error("Must specify at least one file or directory...")

    level = logging.WARNING
    if options.quiet:
        level = logging.FATAL
    elif options.verbose:
        level = logging.INFO

    format = "%(message)s"
    logging.basicConfig(format=format, filename=options.log_file, level=level)

    if options.dry_run:
        logging.info("DRY RUN")

    for arg in args:
        scanpath(arg, options)

if __name__=="__main__":
    sys.exit(main())
