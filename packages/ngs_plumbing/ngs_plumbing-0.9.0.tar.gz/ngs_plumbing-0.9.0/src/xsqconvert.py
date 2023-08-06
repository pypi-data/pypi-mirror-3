#!/usr/bin/env python

#
#   XSQ converter
#

# This file is part of ngs_plumbing.

# ngs_plumbing is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ngs_plumbing is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>.

# Copyright 2012 Laurent Gautier

import argparse
import os
import sys

try:
    import ngs_plumbing.xsq
except ImportError:
    sys.stderr.write('Error: the Python package "h5py" is required but could not be imported. Bye.')
    sys.stderr.flush()
    sys.exit(1)
xsq = ngs_plumbing.xsq

def main():
    parser = argparse.ArgumentParser(
        description = 'Convert XSQ files into less exotic (albeit sometimes also less efficient) formats.')
    parser.add_argument('paths', metavar='XSQ_FILE', nargs='*',
                        help='XSQ files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='directory in which resulting files should be put')
    parser.add_argument('-f', '--format-style',
                        dest = 'output_format',
                        choices = ('FASTA', 'FASTQ'),
                        help = "Style of the format to output to.")
    parser.add_argument('-s', '--data-space',
                        dest = 'data_space',
                        choices = ('base', 'color'),
                        help = "Space to output the data into.")
    parser.add_argument('-E', '--ECC',
                        dest = 'use_ecc',
                        action = 'store_true',
                        help = 'use ECC to get data in base space.')
    parser.add_argument('-i', '--info',
                        dest = 'want_info',
                        action = 'store_true',
                        help = 'Print information about the XSQ file')
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()


    if options.use_ecc and options.data_space == 'color':
        sys.stderr.write('Error: wanting data in color space is not compatible with wanting ECC data.')
        sys.stderr.flush()
        sys.exit(1)


    for f in options.paths:
        if not os.path.exists(f):
            print('Error: Path "%s" does not exist' %f)
            sys.exit(1)

    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            print('Error: destination directory already existing (but not as a directory')
            sys.exit(1)
    else:
        print('Warning: destination directory not existing; creating it.')
        os.mkdir(options.dest_dir)
        
    for f in options.paths:
        xsq_fn = os.path.basename(f)
        sep_i = xsq_fn.rfind(os.path.extsep)
        if sep_i == -1 or (sep_i == (len(xsq_fn) - 1)) or (xsq_fn[(sep_i+1):].lower() != 'xsq'):
            print('XSQ files are expected to have the extension XSQ.')
            sys.exit(1)
        dest_dir = os.path.join(options.dest_dir, xsq_fn[:sep_i])
        os.mkdir(dest_dir)
        if options.want_info:
            xf = xsq.XSQFile(f)
            try:
                mtd = xf.run_metadata
            except KeyError:
                mtd = False
            for field in ('tagdetails', 'lanenumber', 'hdfversion', 'fileversion',
                          'sequencingsamplename', 'sequencingsampledescription',
                          'runname'):
                sys.stdout.write(field)
                sys.stdout.write(': ')
                #import pdb; pdb.set_trace()
                sys.stdout.write(str(getattr(mtd, field, None)))
                sys.stdout.write('\n')
                sys.stdout.flush()
            xf.close()

        if options.output_format == 'FASTA':
            if options.data_space == 'color':
                xsq.automagic_csfasta(f, path_out = dest_dir,
                                      fragment = None, 
                                      buf_size = long(2E6), 
                                      out = sys.stdout)
            else:
                print('--->')   
        else:
            # FASTQ data
            if options.data_space == 'color':
                xsq.automagic_fastq(f, path_out = dest_dir, 
                                    fragment = None, 
                                    buf_size = long(2E6), 
                                    out = sys.stdout,
                                    extension = 'csfq',
                                    cs = True)
            else:
                # base space
                if options.use_ecc:
                    try:
                        xsq.automagic_fastq(f, path_out = dest_dir, 
                                            fragment = None, 
                                            buf_size = long(2E6), 
                                            out = sys.stdout,
                                            cs = False)
                    except KeyError, ke:
                        print('\nError: No base calls for file "%s".' %f)
                else:
                    print('--->')

    if (not options.data_space) or (not options.output_format):
        print('No output format or data space specified, so nothing was done. Goodbye.')

def htmlreport():
    import argparse

    parser = argparse.ArgumentParser(
        description = 'Make an HTML report on XSQ files.')
    parser.add_argument('paths', metavar='XSQ_FILE', nargs='*',
                        help='XSQ files')
    parser.add_argument('-d', '--dir',
                        dest = 'dest_dir',
                        default = '.',
                        help='Directory in which resulting files should be put')
    parser.add_argument('-f', '--force',
                        dest = 'force',
                        action = 'store_true',
                        help = 'Silently force actions such as overwriting files or creating missing directories.')
    parser.add_argument('-p', '--sampling-percentage',
                        dest = 'sample_percent',
                        default = 0.05,
                        type = float,
                        help = 'Percentage of the data to sample (a number between 0 and 1, default: 0.05, that is 5%%).')
    parser.add_argument('-t', '--data-type',
                        dest = 'data_type',
                        default = 'json',
                        help='Data type (default: json).')
    parser.add_argument('-V', '--version',
                        action = 'version',
                        version = ngs_plumbing.__version__)
    options = parser.parse_args()

    for f in options.paths:
        if not os.path.exists(f):
            print('Error: Path "%s" does not exist' %f)
            sys.exit(1)

    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            print('Error: destination directory already existing (but not as a directory')
            sys.exit(1)
    else:
        if options.force:
            sys.stdout.write('Creating directory missing...')
            sys.stdout.flush()
            try:
                os.mkdir(options.dest_dir)
            except OSError, ose:
                sys.stderr.write('\n')
                sys.stderr.write(str(ose))
                sys.stderr.write('\n')
                sys.stderr.flush()
                sys.exit(1)
            sys.stdout.write('done.\n')
            sys.stdout.flush()
        else:
            print('Error: destination directory does not exist.')
            sys.exit(1)
            
    xsq_fn = os.path.basename(f)
    sep_i = xsq_fn.rfind(os.path.extsep)
    if sep_i == -1 or (sep_i == (len(xsq_fn) - 1)) or (xsq_fn[(sep_i+1):].lower() != 'xsq'):
        print('XSQ files are expected to have the extension XSQ.')
        sys.exit(1)
    dest_dir = os.path.join(options.dest_dir, xsq_fn[:sep_i])
    try:
        os.mkdir(dest_dir)
    except OSError, ose:
        sys.stderr.write(str(ose))
        sys.stderr.write('\n')
        sys.stderr.flush()
        sys.exit(1)
    if os.path.exists(options.dest_dir):
        if not os.path.isdir(options.dest_dir):
            print('Error: destination directory already existing (but not as a directory')
            sys.exit(1)
    else:
        print('Warning: destination directory not existing; creating it.')
        os.mkdir(options.dest_dir)

    for f in options.paths:
        xf = xsq.XSQFile(f)
        xsq.make_htmlreport(xf, directory = dest_dir,
                            sample_percent = options.sample_percent,
                            data_type = options.data_type)
        xf.close()

if __name__ == '__main__':
    main()
