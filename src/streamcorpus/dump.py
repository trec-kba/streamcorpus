#!/usr/bin/env python
'''
A command line utility for printing out information from
streamcorpus.Chunk files.

This software is released under an MIT/X11 open source license.

Copyright 2012 Diffeo, Inc.
'''

import os
import sys
import json
import itertools
import collections
from ._chunk import Chunk

def _dump(fpath, args):
    '''
    Reads in a streamcorpus.Chunk file and prints the metadata of each
    StreamItem to stdout
    '''
    if args.count:
        num_stream_items = 0
        num_labeled_stream_items = set()

    for num, si in enumerate(Chunk(path=fpath, mode='rb')):
        if args.limit and num >= args.limit:
            break

        if args.count:
            num_stream_items += 1
            if not args.labels_only:
                continue

        if args.labels_only:
            if si.body.sentences:
                for tagger_id in si.body.sentences:
                    for sent in si.body.sentences[tagger_id]:
                        if args.count and si.stream_id in num_labeled_stream_items:
                            break
                        for tok in sent.tokens:
                            if tok.labels:
                                if args.count:
                                    num_labeled_stream_items.add(si.stream_id)
                                    break
                                else:
                                    print tok.token, tok.labels

        elif not args.show_all:
            si.body = None
            if si.other_content:
                for oc in si.other_content:
                    si.other_content[oc] = None

        elif args.show_content_field and si.body:
            
            print getattr(si.body, args.show_content_field)

        else:
            print si

    if args.count:
        print '%d\t%d\t%s' % (num_stream_items, len(num_labeled_stream_items), fpath)

token_attrs = [
    'token_num',
    'sentence_pos',
    'token',
    'offsets',
    'lemma',
    'pos',
    'entity_type',
    'mention_id',
    'equiv_id',
    'parent_id',
    'dependency_path',
    ]

def _dump_tokens(fpaths, annotator_ids=[]):
    '''
    Read in a streamcorpus.Chunk files and print all tokens in a fixed
    order that enables diffing.

    :param fpaths: iterator over file paths to Chunks

    :paramm annotator_ids: if present, only print tokens with labels
    from one of these annotators
    '''
    print '\t'.join(token_attrs + ['stream_id', 'labels'])
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
            if not si.body.sentences:
                continue
            tagger_ids = si.body.sentences.keys()
            tagger_ids.sort()
            for tagger_id in tagger_ids:
                for sent in si.body.sentences[tagger_id]:
                    for tok in sent.tokens:
                        vals = [repr(getattr(tok, attr))
                                for attr in token_attrs]
                        vals += [si.stream_id]
                        vals += [','.join([label.target_id for label in tok.labels])]
                        line = '\t'.join(vals)
                        found_annotator = False
                        for label in tok.labels:
                            if label.annotator and label.annotator.annotator_id in annotator_ids:
                                found_annotator = True
                                break
                        if found_annotator or not annotator_ids:
                            print line

def _find(fpaths, stream_id):
    '''
    Read in a streamcorpus.Chunk file and if any of its stream_ids
    match stream_id, then print stream_item.body.raw to stdout
    '''
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
            if si.stream_id == stream_id:
                if si.body and si.body.raw:
                    print si.body.raw
                    sys.exit()
                elif si.body:
                    sys.exit('Found %s without si.body.raw' % stream_id)
                else:
                    sys.exit('Found %s without si.body' % stream_id)

def _stats(fpaths):
    '''
    Read streamcorpus.Chunk files and print their stats
    '''
    keys = ['stream_ids', 'num_targets_from_google', 'raw', 'raw_has_targs', 'raw_has_wp', 'media_type', 'clean_html', 'clean_has_targs', 'clean_has_wp',
            'clean_visible', 'labelsets', 'labels', 'labels_has_targs', 'sentences', 'tokens', 'at_least_one_label']
    print '\t'.join(keys)
    for fpath in fpaths:
        #print fpath
        sys.stdout.flush()
        c = collections.Counter()
        labels = collections.Counter()
        for num, si in enumerate( Chunk(path=fpath, mode='rb') ):
            #print si.stream_id
            sys.stdout.flush()
            c['stream_ids'] += 1
            if si.body:
                target_ids = [rec['target_id'] for rec in json.loads( si.source_metadata['google'] )['MENTION']]
                c['num_targets_from_google'] += len(target_ids)
                c['raw'] += int(bool(si.body.raw))
                c['raw_has_targs'] += sum(map(lambda targ: int(bool(targ in repr(si.body.raw))), target_ids))
                c['raw_has_wp'] += int(bool('wikipedia.org' in si.body.raw))
                c['media_type'] += int(bool(si.body.media_type))
                c['clean_html'] += int(bool(si.body.clean_html))
                if si.body.clean_html:
                    c['clean_has_targs'] += sum(map(lambda targ: int(bool(targ in si.body.clean_html.decode('utf8'))), target_ids))
                    c['clean_has_wp'] += int(bool('wikipedia.org' in si.body.clean_html))

                c['clean_visible'] += int(bool(si.body.clean_visible))
                c['labelsets'] += len(si.body.labelsets)
                c['labels'] += sum(map(lambda labelset: len(labelset.labels), si.body.labelsets))
                label_targs = []
                for labelset in si.body.labelsets:
                    label_targs += [label.target_id for label in labelset.labels]
                c['labels_has_targs'] += sum(map(lambda targ: int(bool(targ in label_targs)), target_ids))
                _labels = collections.Counter()
                for sentences in si.body.sentences.values():
                    c['sentences'] += len(sentences)
                    for sent in sentences:
                        for tok in sent.tokens:
                            c['tokens'] += 1
                            for label in tok.labels:
                                _labels[label.annotator.annotator_id] += 1
                #print _labels
                labels += _labels
                c['at_least_one_label'] += int(bool(_labels))
                sys.stdout.flush()

        print '\t'.join([str(c[k]) for k in keys] + ['%s:%d' % it for it in labels.items()])
        #print json.dumps( c, indent=4 )
        #print json.dumps( labels, indent=4 )
        sys.stdout.flush()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path', 
        help='Path to a single chunk file, or directory of chunks, or "-" for receiving paths over stdin')
    parser.add_argument('--stats', action='store_true', default=False,
                        help='print out the .body.raw of a specific stream_id')
    parser.add_argument('--find', dest='find', metavar='STREAM_ID', help='print out the .body.raw of a specific stream_id')
    parser.add_argument('--tokens', action='store_true', 
                        default=False, dest='tokens')
    parser.add_argument('--annotator_id', action='append', default=[],
                        dest='annotator_ids', help='only show tokens that have this annotator_id')
    parser.add_argument('--show-all', action='store_true', 
                        default=False, dest='show_all')
    parser.add_argument('--show-content-field', 
                        default=None, dest='show_content_field')
    parser.add_argument('--count', action='store_true', 
                        default=False, help='print number of StreamItems')
    parser.add_argument('--limit', type=int,
                        default=None, help='Limit the number of StreamItems checked')
    parser.add_argument('--labels-only', action='store_true', 
                        default=False, dest='labels_only')
    args = parser.parse_args()


    ## make input_path into an iterable over path strings
    if args.input_path == '-':
        args.input_path = itertools.imap(lambda line: line.strip(), sys.stdin)

    elif os.path.isdir(args.input_path):
        args.input_path = itertools.imap(lambda fname: os.path.join(args.input_path, fname),
                                         os.listdir(args.input_path))

    else:
        args.input_path = [args.input_path]

    if args.stats:
        _stats(args.input_path)

    elif args.find:
        _find(args.input_path, args.find)

    elif args.tokens:
        _dump_tokens(args.input_path, args.annotator_ids)

    else:
        for fpath in args.input_path:
            _dump(fpath, args)
