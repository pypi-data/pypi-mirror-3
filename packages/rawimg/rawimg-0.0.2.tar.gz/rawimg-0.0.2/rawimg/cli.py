#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import Image

def load(handler, width=256, height=256):
    with handler as f:
        rawdata = f.read()
    imgsize = (width, height)
    return Image.fromstring('L', imgsize, rawdata)

def preview(args):
    width, height = args.size.split('x') 
    img = load(args.infile, int(width), int(height)) 
    img.show()

def save(args):
    width, height = args.size.split('x') 
    img = load(args.infile, int(width), int(height))
    img.save(args.filename)

class RawimgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main():

    parser = RawimgParser()
    subparsers = parser.add_subparsers(title='Commands')

    preview_parser = subparsers.add_parser('preview', help='Preview the image')
    preview_parser.add_argument('infile', type=argparse.FileType('rb'))

    preview_parser.add_argument('-s', dest='size')
    preview_parser.set_defaults(func=preview)
   
    save_parser = subparsers.add_parser('save', 
        help='Saves the image under the given filename')
    save_parser.add_argument('infile', type=argparse.FileType('rb'))
    save_parser.add_argument('-s', dest='size')
    save_parser.add_argument('-o', dest='filename')
    save_parser.set_defaults(func=save)

    args = parser.parse_args()
    args.func(args)

