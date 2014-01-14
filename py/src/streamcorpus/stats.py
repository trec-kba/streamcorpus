#!/usr/bin/env python
'''
A command line utility for printing out information from
streamcorpus.Chunk files.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''
from __future__ import absolute_import
import os
import sys
import json
import logging
import itertools
import collections
from streamcorpus._chunk import Chunk
from streamcorpus.ttypes import OffsetType, Token, EntityType, MentionType

from streamcorpus.ttypes import StreamItem as StreamItem_v0_3_0
from streamcorpus.ttypes_v0_1_0 import StreamItem as StreamItem_v0_1_0
from streamcorpus.ttypes_v0_2_0 import StreamItem as StreamItem_v0_2_0

versioned_classes = {
    'v0_3_0': StreamItem_v0_3_0,
    'v0_2_0': StreamItem_v0_2_0,
    'v0_1_0': StreamItem_v0_1_0,
    }

filter_classes = {
    'entity_type' : EntityType,
    'mention_type' : MentionType,
}

def _count_filter_types(fpath, filter_by, filter_values, message_class):
    all_counter = collections.defaultdict(collections.Counter)

    for num, si in enumerate(Chunk(path=fpath, mode='rb', message=message_class)):
        print 'counting entity types for StreamItem', num
        if si.body.sentences:
            for tagger_id, sentences in si.body.sentences.items():
                sentences_counter = collections.Counter(_filter_token_attr(sentences, filter_by, filter_values))
                all_counter[tagger_id].update(sentences_counter)
                print '\t counting entity types for tagger id', tagger_id
                for filter_value in filter_values:
                    print '\t\t', filter_classes[filter_by]._VALUES_TO_NAMES[filter_value], sentences_counter[filter_value]

    print 'counting entity types for all StreamItems'
    for tagger_id, counter in all_counter.items():
        print '\t', tagger_id
        for filter_value in filter_values:
            print '\t\t', filter_classes[filter_by]._VALUES_TO_NAMES[filter_value], counter[filter_value]

def _filter_token_attr(sentences, attr, filter_types):
    for sentence in sentences:
        for tok in sentence.tokens:
            value = getattr(tok, attr)
            if value:
                yield getattr(tok, attr)

def main():
    logger = logging.getLogger('streamcorpus')
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path', 
        nargs='*',
        default=[],
        help='Paths to a chunk files, or directory of chunks, or "-" for receiving paths over stdin'
    )
    parser.add_argument('--version', default='v0_3_0')
    parser.add_argument(
        '--entity-type',
        dest='entity_type',
        nargs='*',
        help='Return count of all tokens of specified types. Default is all types'
    )
    parser.add_argument(
        '--mention-type',
        dest='mention_type',
        nargs='*',
        help='Return count of all tokens of specified mention types. Default is all mention types'
    )
    args = parser.parse_args()

    if args.version not in versioned_classes:
        sys.exit('--version=%r is not in "%s"' \
                     % (args.version, '", "'.join(versioned_classes.keys())))

    message_class = versioned_classes[args.version]

    ## make input_path into an iterable over path strings
    paths = []
    for ipath in args.input_path:
        if ipath == '-':
            paths.extend(itertools.imap(lambda line: line.strip(), sys.stdin))
        elif os.path.isdir(ipath):
            paths.extend(
                map(lambda fname: os.path.join(args.input_path, fname),
                    os.listdir(args.input_path)))
        else:
            paths.append(ipath)
    args.input_path = paths
    
    for filter_class in filter_classes:
        arg = getattr(args, filter_class)
        if arg is not None:
            if len(arg) == 0:
                filter_values = filter_classes[filter_class]._VALUES_TO_NAMES.keys()
            else:
                filter_values = [filter_classes[filter_class]._NAMES_TO_VALUES[name] for name in arg]
            for fpath in args.input_path:
                _count_filter_types(fpath, filter_class, filter_values, message_class)

if __name__ == '__main__':
    main()
