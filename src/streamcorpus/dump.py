#!/usr/bin/env python
'''
Reads in a streamcorpus.Chunk file and prints the metadata of each
StreamItem to stdout
'''

from ._chunk import Chunk

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('--show-content-items', action='store_true', 
                        default=False, dest='show_content_items')
    args = parser.parse_args()

    for si in Chunk(file_obj=open(args.input_path)):
        if not args.show_content_items:
            si.body = None
            if si.other_content:
                for oc in si.other_content:
                    si.other_content[oc] = None
        print si
