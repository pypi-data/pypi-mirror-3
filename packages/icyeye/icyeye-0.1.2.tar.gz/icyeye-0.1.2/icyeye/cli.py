#!/usr/bin/env python
"""Command-line interface for icyeye functionality"""
from optparse import OptionParser
from os import path
import sys

from icyeye import make_css_images_inline, CssFileError


def main():
    parser = OptionParser(
        usage="%prog [options] <input CSS file> <absolute URL of CSS file> "
            "<ouptut file>"
        )
    parser.add_option(
        "-m",
        "--max-image-size", 
        type="int",
        dest="max_image_size",
        help="The size (in bytes) which images must be under to be encoded",
        )
    
    options, arguments = parser.parse_args()
    
    if len(arguments) != 3:
        print "%s takes exactly three arguments!\n" % parser.get_prog_name()
        print parser.get_usage()
        sys.exit(1)
    
    css_file_path = path.abspath(path.expanduser(arguments[0]))
    css_file_url = arguments[1]
    output_file_name = path.abspath(path.expanduser(arguments[2]))
    
    if not path.exists(css_file_path):
        print "'%s' cannot be found - aborting conversion" % css_file_path
        sys.exit(2)
    
    output_dir = path.dirname(output_file_name)
    if not path.exists(output_dir):
        print "The directory to contain the output file '%s' does not exist " \
            "- aborting conversion" % output_dir
        sys.exit(2)
    
    print "Converting '%s'" % css_file_path
    
    try:
        converted_css = make_css_images_inline(
            css_file_path, css_file_url, options.max_image_size)
    except CssFileError, exc:
        print str(exc)
        sys.exit(3)
    except (IOError, OSError), exc:
        print str(exc)
        sys.exit(4)
    except Exception, exc:
        print "An unexpected error occurred: %s" % exc
        sys.exit(100)
        
    output_file = None
    try:
        output_file = open(output_file_name, "w")
        output_file.write(converted_css)
    finally:
        if output_file is not None:
            output_file.close()
    
    print "Conversion complete"
    
if __name__ == "__main__":
    main()
