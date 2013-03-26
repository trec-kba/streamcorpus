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
from _chunk import Chunk, StreamItem, StreamItem_v0_1_0
from . import OffsetType

versioned_classes = {
    "v0.2.0": StreamItem,
    "v0.1.0": StreamItem_v0_1_0,
    }

def _dump(fpath, args):
    '''
    Reads in a streamcorpus.Chunk file and prints the metadata of each
    StreamItem to stdout
    '''
    if args.count:
        num_stream_items = 0
        num_labeled_stream_items = set()

    global message_class
    for num, si in enumerate(Chunk(path=fpath, mode='rb', message=message_class)):
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
                                    print si.stream_id, tok.token.decode('utf8').encode('utf8'), tok.labels

        elif not args.show_all:
            si.body = None
            if getattr(si, 'other_content', None):
                for oc in si.other_content:
                    si.other_content[oc] = None

        elif args.show_content_field and si.body:
            
            print getattr(si.body, args.show_content_field)

        else:
            print si

    if args.count:
        print '%d\t%d\t%s' % (num_stream_items, len(num_labeled_stream_items), fpath)


def _dump_ratings(fpaths, annotator_ids=[], include_header=False):
    '''
    Read in a streamcorpus.Chunk files and print all Rating objects as
    tab-separated values

    :param fpaths: iterator over file paths to Chunks

    :paramm annotator_ids: if present, only print Rating objects from
    from one of these annotators
    '''
    print '\t'.join(['annotator_id', 'target_id', 'stream_id', 'num_mentions', 'mentions'])
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
            for annotator_id, ratings in si.ratings.items():
                if annotator_ids and annotator_id not in annotator_ids:
                    ## skip ratings not created by one of
                    ## annotator_ids
                    continue
                for rating in ratings:
                    assert rating.annotator.annotator_id == annotator_id, \
                        (rating.annotator.annotator_id, annotator_id)
                    print '\t'.join([
                            annotator_id,
                            rating.target.target_id,
                            si.stream_id,
                            str(len(rating.mentions)),
                            json.dumps(rating.mentions),                            
                            ])



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
    global message_class
    print '\t'.join(token_attrs + ['stream_id', 'labels'])
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb', message=message_class):
            if not si.body:
                print 'no body: %s' % si.stream_id
                continue
            if not si.body.sentences:
                print 'no body.sentences: %s' % si.stream_id
                continue
            tagger_ids = si.body.sentences.keys()
            tagger_ids.sort()
            for tagger_id in tagger_ids:
                for sent in si.body.sentences[tagger_id]:
                    for tok in sent.tokens:
                        vals = []
                        for attr in token_attrs:
                            val = getattr(tok, attr)
                            if isinstance(val, str):
                                vals.append( val.decode('utf8').encode('utf8') )
                            else:
                                vals.append( repr(val) )

                        vals += [si.stream_id]

                        target_ids = []
                        for labels in tok.labels.values():
                            for label in labels:
                                target_ids.append(label.target.target_id)
                        vals += [','.join(target_ids)]

                        line = '\t'.join(vals)
                        found_annotator = False
                        for annotator_id in tok.labels:
                            if annotator_id in annotator_ids:
                                found_annotator = True
                                break
                        if found_annotator or not annotator_ids:
                            print line


def verify_offsets(fpaths):
    '''
    Read in a streamcorpus.Chunk files and verify that the 'value'
    property in each offset matches the actual text at that offset.

    :param fpaths: iterator over file paths to Chunks
    '''
    global message_class
    for fpath in fpaths:
        print fpath
        num_valid_line_offsets = 0
        num_valid_byte_offsets = 0
        num_valid_label_offsets = 0
        for si in Chunk(path=fpath, mode='rb', message=message_class):
            if not si.body:
                print 'no body: %s' % si.stream_id
                continue
            if not si.body.sentences:
                print 'no body.sentences: %s' % si.stream_id
                continue
            for tagger_id in si.body.sentences:
                for sent in si.body.sentences[tagger_id]:
                    for tok in sent.tokens:
                        if OffsetType.BYTES in tok.offsets:
                            off = tok.offsets[OffsetType.BYTES]
                            
                            text = getattr(si.body, off.content_form)
                            val = text[ off.first : off.first + off.length]

                            if off.value and val != off.value:
                                window = 20
                                print 'ERROR:  %r != %r in %r' % (off.value, val, text[ off.first - window : off.first + off.length + window])

                            else:
                                num_valid_byte_offsets += 1

                            for labels in tok.labels.values():
                                for label in labels:
                                    if OffsetType.BYTES in label.offsets:
                                        ## get the offset from the label, and compare the value
                                        off_label = label.offsets[OffsetType.BYTES]
                                        if off_label.value and val != off_label.value:
                                            window = 20
                                            print 'ERROR:  %r != %r in %r' % (off.value, val, text[ off.first - window : off.first + off.length + window])
                                        else:
                                            num_valid_label_offsets += 1


                        if OffsetType.LINES in tok.offsets:
                            off = tok.offsets[OffsetType.LINES]
                            
                            text = getattr(si.body, off.content_form)
                            def get_val(text, start, end):
                                return '\n'.join( text.splitlines()[ start : end ] )

                            val_lines = get_val(text, off.first, off.first + off.length)

                            if not off.value:
                                print 'UNKNOWN: .value not provided in offset'
                                continue

                            elif off.value and off.value not in val_lines:
                                window = 3
                                print 'ERROR:  %r != %r in %r' % (off.value, val_lines, get_val(text, off.first - window, off.first + off.length + window))

                            else:
                                num_valid_line_offsets += 1

                            for labels in tok.labels.values():
                                for label in labels:
                                    if OffsetType.LINES in label.offsets:
                                        ## get the offset from the label, and compare the value
                                        off_label = label.offsets[OffsetType.LINES]
                                        if off_label.value and val != off_label.value:
                                            window = 20
                                            print 'ERROR:  %r != %r in %r' % (off.value, val, text[ off.first - window : off.first + off.length + window])
                                        else:
                                            num_valid_label_offsets += 1

        print '''
num_valid_byte_offsets: %d
num_valid_line_offsets: %d
num_valid_label_offsets: %d
''' % (num_valid_byte_offsets, num_valid_line_offsets, num_valid_label_offsets)


def _find(fpaths, stream_id):
    '''
    Read in a streamcorpus.Chunk file and if any of its stream_ids
    match stream_id, then print stream_item.body.raw to stdout
    '''
    global message_class
    sys.stderr.write('hunting for %r\n' % stream_id)
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb', message=message_class):
            if si.stream_id == stream_id:
                if si.body and si.body.raw:
                    print si.body.raw
                    sys.exit()
                elif si.body:
                    sys.exit('Found %s without si.body.raw' % stream_id)
                else:
                    sys.exit('Found %s without si.body' % stream_id)

def _show_fields(fpaths, fields):
    '''
    streamcorpus.Chunk files and display each field specified in 'fields'
    '''
    global message_class
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb', message=message_class):
            for field in fields:
                prop = si
                for prop_name in field.split('.'):
                    prop = getattr(prop, prop_name, None)
                    if not prop: break
                if prop:
                    print field, prop



def _find_missing_labels(fpaths, annotator_ids, component):
    '''
    Read in a streamcorpus.Chunk file and if any of its stream_ids
    match stream_id, then print stream_item.body.raw to stdout
    '''
    global message_class
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb', message=message_class):
            if not si.body:
                print 'no body on %s %r' % (si.stream_id, si.abs_url)
                continue
            if not si.body.raw:
                print 'no body.raw on %s %r' % (si.stream_id, si.abs_url)
                continue

            found_annotator = False
            for tagger_id in si.body.sentences:
                for sent in si.body.sentences[tagger_id]:
                    for tok in sent.tokens:
                        for label in tok.labels:
                            if label.annotator and label.annotator.annotator_id in annotator_ids:
                                found_annotator = True
                                break
                        if found_annotator:
                            break
                    if found_annotator:
                        break
                if found_annotator:
                    break
            ## either we found_annotator or read all tokens
            if found_annotator:
                print '## success with %s' % si.stream_id
            else:
                print 'failed to find annotator_id in %r for %s' % (annotator_ids, si.stream_id)
                if component == 'stream_id':
                    print si.stream_id
                else:
                    print getattr(si.body, component)

def _stats(fpaths):
    '''
    Read streamcorpus.Chunk files and print their stats
    '''
    global message_class
    keys = ['stream_ids', 'num_targets_from_google', 'raw', 'raw_has_targs', 'raw_has_wp', 'media_type', 'clean_html', 'clean_has_targs', 'clean_has_wp',
            'clean_visible', 'labelsets', 'labels', 'labels_has_targs', 'sentences', 'tokens', 'at_least_one_label']
    print '\t'.join(keys)
    for fpath in fpaths:
        #print fpath
        sys.stdout.flush()
        c = collections.Counter()
        labels = collections.Counter()
        for num, si in enumerate( Chunk(path=fpath, mode='rb', message=message_class) ):
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
    parser.add_argument(
        '--find-missing', dest='find_missing', action='store_true', default=False,
        help='print out the .body.<content> of any stream_item that has no tokens with a label in annotator_ids')
    parser.add_argument(
        '--component', dest='component', metavar='raw|clean_html|clean_visible', 
        help='print out the .body.<component>')
    parser.add_argument('--version', default='v0.2.0')
    parser.add_argument('--tokens', action='store_true', 
                        default=False, dest='tokens')
    parser.add_argument('--ratings', action='store_true', default=False)
    parser.add_argument('--include-header', action='store_true', default=False, dest='include_header')
    parser.add_argument('--annotator_id', action='append', default=[],
                        dest='annotator_ids', help='only show tokens that have this annotator_id')
    parser.add_argument('--show-all', action='store_true', 
                        default=False, dest='show_all')
    parser.add_argument('--show-content-field', 
                        default=None, dest='show_content_field')
    parser.add_argument('--field', default=[], 
                        action='append', dest='fields',
                        help='".foo.bar" will yield StreamItem.foo.bar, if it exists.  Can request multiple --field .foo.bar1 --field .foo.bar2 ')
    parser.add_argument('--count', action='store_true', 
                        default=False, help='print number of StreamItems')
    parser.add_argument('--limit', type=int,
                        default=None, help='Limit the number of StreamItems checked')
    parser.add_argument('--labels-only', action='store_true', 
                        default=False, dest='labels_only')
    parser.add_argument('--verify-offsets', action='store_true', 
                        default=False, dest='verify_offsets')
    args = parser.parse_args()

    if args.version not in versioned_classes:
        sys.exit('--version=%r is not in "%s"' \
                     % (args.version, '", "'.join(versioned_classes.keys())))

    global message_class
    message_class = versioned_classes[args.version]

    ## make input_path into an iterable over path strings
    if args.input_path == '-':
        args.input_path = itertools.imap(lambda line: line.strip(), sys.stdin)

    elif os.path.isdir(args.input_path):
        args.input_path = map(lambda fname: os.path.join(args.input_path, fname),
                                         os.listdir(args.input_path))

    else:
        args.input_path = [args.input_path]

    ## now actually do whatever was requested
    if args.fields:
        _show_fields(args.input_path, args.fields)

    elif args.stats:
        _stats(args.input_path)

    elif args.find:
        _find(args.input_path, args.find)

    elif args.tokens:
        _dump_tokens(args.input_path, args.annotator_ids)

    elif args.find_missing:
        _find_missing_labels(args.input_path, args.annotator_ids, args.component)

    elif args.verify_offsets:
        verify_offsets(args.input_path)

    elif args.ratings:
        _dump_ratings(args.input_path, 
                      annotator_ids=args.annotator_ids,
                      include_header=args.include_header)

    else:
        for fpath in args.input_path:
            _dump(fpath, args)
