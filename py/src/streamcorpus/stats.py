#!/usr/bin/env python
'''
Command is $ streamcorpus_stats
A command line utility for printing out information from
streamcorpus.Chunk files. This command prints out stats about the tokens,
including counts of different token types

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
from streamcorpus.ttypes import Token, EntityType, MentionType

from streamcorpus.ttypes import StreamItem as StreamItem_v0_3_0
from streamcorpus.ttypes_v0_1_0 import StreamItem as StreamItem_v0_1_0
from streamcorpus.ttypes_v0_2_0 import StreamItem as StreamItem_v0_2_0

versioned_classes = {
    'v0_3_0': StreamItem_v0_3_0,
    'v0_2_0': StreamItem_v0_2_0,
    'v0_1_0': StreamItem_v0_1_0,
    }

FILTER_CLASSES = {
    'entity_type' : EntityType,
    'mention_type' : MentionType,
}
OUTPUT_MSGS = {
    'si' : '\ncounting for StreamItem {num}',
    'tagger_id' : '\tcounting for tagger id {tagger_id}',
    'count' : '\t\t{filter_by} {filter_value} {count}',
}

def _process_filters(fpath, all_filters, message_class, tagger_ids):
    """
    takes in
    fpath - streamitem chunk file to read from
    all_filters - dictionary of {
        attribute to filter by (entity_type, custom_entity_type, etc.) : list
            of values to filter against
    }
    message_class - StreamItem version to use
    tagger_ids - list of tagger ids to dump streamitems for. If none, then all
        tagger ids are dumped

    outputs to stdout, with full count of file at tail
    counting for StreamItem #
        counting for tagger id <tagger id>
            <attribute to filter by> <filter value> <count>
    """
    all_counter = collections.defaultdict(collections.Counter)

    for num, si in enumerate(Chunk(path=fpath, mode='rb', message=message_class)):
        print OUTPUT_MSGS['si'].format(num=num)
        if si.body.sentences:
            for tagger_id, sentences in si.body.sentences.iteritems():
                if tagger_ids is None or tagger_id in tagger_ids:
                    print OUTPUT_MSGS['tagger_id'].format(tagger_id=tagger_id)
                    for filter_by, filter_values in all_filters.iteritems():
                        sentences_counter = collections.Counter(
                            _filter_token_attr(sentences, filter_by, filter_values)
                        )
                        all_counter[tagger_id].update(sentences_counter)
                        _print_filter_counts(sentences_counter, filter_by, filter_values)

    print OUTPUT_MSGS['si'].format(num='all')
    for tagger_id, counter in all_counter.items():
        if tagger_ids is None or tagger_id in tagger_ids:
            print OUTPUT_MSGS['tagger_id'].format(tagger_id=tagger_id)
            for filter_by, filter_values in all_filters.iteritems():
                _print_filter_counts(counter, filter_by, filter_values)

def _filter_token_attr(sentences, attr, filter_types):
    """
    generator to return the value of a specified attribute of 
    all tokens in a group of sentences
    """
    for sentence in sentences:
        for tok in sentence.tokens:
            value = getattr(tok, attr)
            if value in filter_types:
                yield getattr(tok, attr)

def _print_filter_counts(counter, filter_by, filter_values):
    """
    given a counter, an attribute to filter by, and the values to filter
    against, print a line with counts of the specified filter_values, formatted
    by OUTPUT_MSGS['count']
    """
    for filter_value in filter_values:
        if filter_by in FILTER_CLASSES:
            formatted_filter_value = FILTER_CLASSES[filter_by]._VALUES_TO_NAMES[filter_value]
        else:
            formatted_filter_value = filter_value
        print OUTPUT_MSGS['count'].format(filter_by=filter_by, 
                filter_value=formatted_filter_value, 
                count=counter[filter_value])

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
        '--custom-entity-type',
        dest='custom_entity_type',
        nargs='+',
        help='Return counts of all tokens of specified custom entity types. Must specify at least one.'
    )
    parser.add_argument(
        '--mention-type',
        dest='mention_type',
        nargs='*',
        help='Return count of all tokens of specified mention types. Default is all mention types'
    )
    parser.add_argument(
        '--tagger-ids',
        dest='tagger_ids',
        nargs='+',
        help='Return results for specified tagger ids. Must specify at least one if used. Default is all tagger ids'
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
    
    # parse out user-specified filters and filter values (Ex: --entity-type PER)
    # or use defaults
    all_filters = {}
    for filter_class in FILTER_CLASSES:
        arg = getattr(args, filter_class)
        if arg is not None:
            if len(arg) == 0:
                filter_values = FILTER_CLASSES[filter_class]._VALUES_TO_NAMES.keys()
            else:
                filter_values = [FILTER_CLASSES[filter_class]._NAMES_TO_VALUES[name] for name in arg]
            all_filters[filter_class] = filter_values

    custom_entity_filters = args.custom_entity_type
    if custom_entity_filters:
        all_filters['custom_entity_type'] = custom_entity_filters

    for fpath in args.input_path:
        _process_filters(fpath, all_filters, message_class, args.tagger_ids)


if __name__ == '__main__':
    main()
