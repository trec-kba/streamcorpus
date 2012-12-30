#!/usr/bin/env python
'''
A command line utility for printing out information from
streamcorpus.Chunk files.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

import os
import sys
from ._chunk import Chunk

def _dump(fpath, args):
    '''
    Reads in a streamcorpus.Chunk file and prints the metadata of each
    StreamItem to stdout
    '''
    if args.count:
        num = 0

    for si in Chunk(path=fpath, mode='rb'):
        if args.count:
            num += 1
            continue
        if args.tokens_only:
            if si.body.sentences:
                for tagger_id in si.body.sentences:
                    for sent in si.body.sentences[tagger_id]:
                        for tok in sent.tokens:
                            if tok.labels:
                                print tok.token, tok.labels

        if not args.show_content_items:
            si.body = None
            if si.other_content:
                for oc in si.other_content:
                    si.other_content[oc] = None
        print si

    if args.count:
        print num

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path', 
        help='Path to a single chunk file, or directory of chunks, or "-" for receiving paths over stdin')
    parser.add_argument('--show-content-items', action='store_true', 
                        default=False, dest='show_content_items')
    parser.add_argument('--count', action='store_true', 
                        default=False, help='print number of StreamItems')
    parser.add_argument('--tokens-only', action='store_true', 
                        default=False, dest='tokens_only')
    args = parser.parse_args()

    if args.input_path == '-':
        for fpath in sys.stdin:
            _dump(fpath.strip(), args)

    elif os.path.isdir(args.input_path):
        for fname in os.listdir(args.input_path):
            fpath = os.path.join(args.input_path, fname)
            _dump(fpath, args)

    else:
        _dump(args.input_path, args)
