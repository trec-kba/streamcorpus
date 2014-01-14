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

def _count_entity_types(fpath, entity_types, message_class):
    all_counter = collections.defaultdict(collections.Counter)

    for num, si in enumerate(Chunk(path=fpath, mode='rb', message=message_class)):
        print 'counting entity types for StreamItem', num
        if si.body.sentences:
            for tagger_id, sentences in si.body.sentences.items():
                sentences_counter = collections.Counter(_token_iter(sentences, entity_types))
                all_counter[tagger_id].update(sentences_counter)
                print '\t counting entity types for tagger id', tagger_id
                for entity_type in entity_types:
                    print '\t\t', EntityType._VALUES_TO_NAMES[entity_type], sentences_counter[entity_type]

    print 'counting entity types for all StreamItems'
    for tagger_id, counter in all_counter.items():
        print '\t', tagger_id
        for entity_type in entity_types:
            print '\t\t', EntityType._VALUES_TO_NAMES[entity_type], counter[entity_type]

def _token_iter(sentences, entity_types):
    for sentence in sentences:
        for tok in sentence.tokens:
            if tok.entity_type in entity_types:
                yield tok.entity_type

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
        '--count-entity-types',
        dest='count_entity_types',
        nargs='*',
        help='Return count of all tokens of specified types. Default is all types'
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
    
    if args.count_entity_types is not None:
        if len(args.count_entity_types) == 0:
            count_entity_types = EntityType._VALUES_TO_NAMES.keys()
        else:
            count_entity_types = [EntityType._NAMES_TO_VALUES[name] for name in args.count_entity_types]
        for fpath in args.input_path:
            _count_entity_types(fpath, count_entity_types, message_class)         

if __name__ == '__main__':
    main()
