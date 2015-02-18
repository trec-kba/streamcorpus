#!/usr/bin/env python
'''Print information from a chunk file.

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.

:program:`streamcorpus_dump` prints information on a
:class:`streamcorpus.Chunk` file.  Basic usage is:

.. code-block:: bash

    streamcorpus_dump --show-all input.sc

'''
from __future__ import absolute_import
import os
import sys
import json
import logging
import itertools
import collections
from operator import itemgetter

from streamcorpus._chunk import Chunk as _Chunk
from streamcorpus._cbor_chunk import CborChunk
from streamcorpus.ttypes import OffsetType, Token, EntityType, MentionType

from streamcorpus.ttypes import StreamItem as StreamItem_v0_3_0
from streamcorpus.ttypes_v0_1_0 import StreamItem as StreamItem_v0_1_0
from streamcorpus.ttypes_v0_2_0 import StreamItem as StreamItem_v0_2_0

versioned_classes = {
    'v0_3_0': StreamItem_v0_3_0,
    'v0_2_0': StreamItem_v0_2_0,
    'v0_1_0': StreamItem_v0_1_0,
    }


message_class = StreamItem_v0_3_0


# Wrap the Chunk file constructor locally so we can honor version
# setting more easily.
def Chunk(*args, **kwargs):
    kwargs['message'] = message_class
    return _Chunk(*args, **kwargs)


def Token_repr(tok, limit=50, newlineSplitFields=False, indent=1, splitter=', '):
    assert isinstance(tok, Token)
    fields = []
    for name in tok.__slots__:
        v = getattr(tok, name)
        if v is None:
            continue
        if (name in ('mention_id', 'equiv_id', 'parent_id')) and (v == -1):
            continue  # the no-value int value.
        if ((name == 'offsets') or (name == 'labels')) and not v:
            continue  # probably empty dict: {}
        if name == 'entity_type':
            if v == -1:
                continue
            fields.append('%s=%s' % (name, EntityType._VALUES_TO_NAMES[v]))
        elif name == 'mention_type':
            if v == -1:
                continue
            fields.append('%s=%s' % (name, MentionType._VALUES_TO_NAMES[v]))
        else:
            fields.append('%s=%s' % (name, smart_repr_trim(v, limit=limit, newlineSplitFields=newlineSplitFields, indent=indent+1)))
    return 'Token(' + splitter.join(fields) + ')'
    

# map from type to function
_better_repr_functions = [
    (Token, Token_repr),
]


def smart_repr_trim(ob, limit=50, newlineSplitFields=False, indent=1, print_id=False):
    '''
    returns repr(ob), unless ob is a string that is too long
    '''
    if isinstance(ob, basestring):
        if len(ob) > limit:
            suffix = '...len(%d)' % len(ob)
            prefix = ob[0:limit-len(suffix)]
            if print_id:
                return '({0:x}){1}'.format(id(ob), repr(prefix) + suffix)
            else:
                return repr(prefix) + suffix
    return smart_repr(ob, limit=limit, newlineSplitFields=newlineSplitFields, indent=indent, print_id=print_id)


def smart_repr(x, limit=50, newlineSplitFields=False, indent=1, print_id=False):
    '''
    In case of long fields, print: fieldName='blahblahblhah...'len(9999)
    '''
    if newlineSplitFields:
        splitter = ',\n' + ('  ' * indent)
    else:
        splitter = ', '

    for xtype, xrepr in _better_repr_functions:
        if isinstance(x, xtype):
            return xrepr(x, limit=limit, newlineSplitFields=newlineSplitFields, indent=indent, splitter=splitter)

    if hasattr(x, '__slots__'):
        vals = ['%s=%s' % (key, smart_repr_trim(getattr(x,key), limit=limit, newlineSplitFields=newlineSplitFields, indent=indent+1, print_id=print_id)) for key in x.__slots__]
    elif isinstance(x, list):
        return '[%s]' % splitter.join(map(lambda y: smart_repr(y, limit, newlineSplitFields, indent+1, print_id=print_id), x))
    elif isinstance(x, dict):
        vals = ['%s: %s' % (repr(k),smart_repr(v,limit,newlineSplitFields,indent+1, print_id=print_id)) for k,v in x.iteritems()]
        return '{' + splitter.join(vals) + '}'
    else:
        # Right now this is how we split on primitives vs other objects.
        # Thrift objects all helpfully generate __slots__, but it might be useful to
        # extend smart_repr to other non-thrift non-primitive objects.
        if print_id:
            return '({0:x}){1!r}'.format(id(x), x)
        else:
            return repr(x)
    if print_id:
        return '%s(%x)(%s)' % (x.__class__.__name__, id(x), splitter.join(vals))
    else:
        return '%s(%s)' % (x.__class__.__name__, splitter.join(vals))

def _dump(fpath, args):
    '''
    Reads in a streamcorpus.Chunk file and prints the metadata of each
    StreamItem to stdout
    '''
    if args.count:
        num_stream_items = 0
        num_labeled_stream_items = set()

    stats = None
    if args.stats:
        stats = {}

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
                    if tagger_id not in args.tagger_ids:
                        continue
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

        elif args.print_url:
            if si.original_url:
                print si.original_url
            if si.abs_url and (si.abs_url != si.original_url):
                print si.abs_url

        elif not (args.show_all or args.smart_dump):
            si.body = None
            if getattr(si, 'other_content', None):
                for oc in si.other_content:
                    si.other_content[oc] = None

        elif args.show_content_field and si.body:
            
            print getattr(si.body, args.show_content_field)

        elif args.smart_dump:

            vals = []
            for fieldName in si.__slots__:
                vals.append(fieldName + '=' + smart_repr(getattr(si,fieldName), newlineSplitFields=True, indent=2, limit=100))
            print '%s(%s)' % (si.__class__.__name__, ',\n  '.join(vals))

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
                    columns = [
                        annotator_id,
                        rating.target.target_id,
                        si.stream_id,
                    ]
                    if rating.mentions:
                        columns.append(str(len(rating.mentions)))
                        columns.append(json.dumps(rating.mentions))
                    print '\t'.join(columns)



token_attrs = [
    'token_num',
    'sentence_pos',
    'token',
    'offsets',
    'lemma',
    'pos',
    'mention_type',
    'entity_type',
    'mention_id',
    'equiv_id',
    'parent_id',
    'dependency_path',
    ]

def _dump_tokens(fpaths, annotator_ids=[], filter_tagger_ids=[]):
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
            if not si.body:
                print 'no body: %s' % si.stream_id
                continue
            if not si.body.sentences:
                print 'no body.sentences: %s' % si.stream_id
                continue
            tagger_ids = si.body.sentences.keys()
            tagger_ids.sort()
            for tagger_id in tagger_ids:
                if filter_tagger_ids and tagger_id not in filter_tagger_ids:
                    continue
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
    for fpath in fpaths:
        print fpath
        num_valid_line_offsets = 0
        num_valid_byte_offsets = 0
        num_valid_label_offsets = 0
        for si in Chunk(path=fpath, mode='rb'):
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


def _find(fpaths, stream_id, dump_binary_stream_item=False):
    '''
    Read in a streamcorpus.Chunk file and if any of its stream_ids
    match stream_id, then print stream_item.body.raw to stdout
    '''
    sys.stderr.write('hunting for %r\n' % stream_id)
    offsets = None
    if "#" in stream_id:
        stream_id, offsets = stream_id.split('#')
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
            if si.stream_id == stream_id:
                if dump_binary_stream_item:
                    o_chunk = Chunk(file_obj=sys.stdout, mode='wb')
                    o_chunk.add(si)
                    o_chunk.close()
                    sys.exit()
                elif not offsets and si.body and si.body.raw:
                    print si.body.raw
                    sys.exit()
                elif offsets and si.body and (si.body.clean_html or si.body.clean_visible):
                    if si.body.clean_html:
                        ## prefer using clean_html, if available
                        text = si.body.clean_html
                    else:
                        text = si.body.clean_visible
                    offsets = offsets.split(',')
                    offset_type = set(map(itemgetter(0), offsets))
                    assert len(offset_type) == 1, 'mixed b|c!?: %r' % offsets
                    assert offset_type in (set(['']), set(['b']), set(['c'])), offset_type
                    is_bytes = bool( offset_type != set(['c']) )
                    if not is_bytes:
                        text = text.decode('utf8')
                    for rng in offsets:
                        first, last = rng.split('-')
                        first, last = int(first[1:]), int(last)
                        print text[first:last]
                        
                elif si.body:
                    sys.exit('Found %s without si.body.raw' % stream_id)
                else:
                    sys.exit('Found %s without si.body' % stream_id)

def _show_fields(fpaths, fields, len_fields):
    '''
    streamcorpus.Chunk files and display each field specified in 'fields'
    '''
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
            output = []
            for field in fields:
                prop = si
                for prop_name in field.split('.'):
                    prop = getattr(prop, prop_name, None)
                    if not prop: break
                if prop:
                    if not isinstance(prop, basestring):
                        prop = repr(prop)
                    output.append( '%s: %s' % (field, prop) )
            
            for field in len_fields:
                prop = si
                for prop_name in field.split('.'):
                    prop = getattr(prop, prop_name, None)
                    if not prop: break
                if prop:
                    output.append('%s: %d' % (field, len(prop)))
            sys.stdout.write('%s\n' % ' '.join(output))
            sys.stdout.flush()


def _find_missing_labels(fpaths, annotator_ids, component):
    '''
    Read in a streamcorpus.Chunk file and if any of its stream_ids
    match stream_id, then print stream_item.body.raw to stdout
    '''
    for fpath in fpaths:
        for si in Chunk(path=fpath, mode='rb'):
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


def _tagger_stats(args, fpaths):
    '''
    Produce stats that indicates the size of data from each
    tagger.
    '''
    for fpath in fpaths:
        print fpath
        for i, si in enumerate(Chunk(path=fpath, mode='rb')):
            if args.limit and i >= args.limit:
                break
            print '  %s' % si.stream_id
            for tagger, data in si.body.sentences.iteritems():
                print '    %s => %d' % (tagger, len(repr(data)))
            sys.stdout.flush()


def _stats(fpaths):
    '''
    Read streamcorpus.Chunk files and print their stats
    '''
    keys = ['stream_ids', 'num_targets_from_google', 'raw', 'raw_has_targs', 'raw_has_wp', 'media_type', 'clean_html', 'clean_has_targs', 'clean_has_wp',
            'clean_visible', 'labelsets', 'labels', 'labels_has_targs', 'sentences', 'tokens', 'at_least_one_label']
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
                if 'google' in si.source_metadata:
                    target_ids = [rec['target_id'] for rec in json.loads( si.source_metadata['google'] )['MENTION']]
                else:
                    target_ids = []
                c['num_targets_from_google'] += len(target_ids)
                c['raw'] += int(bool(si.body.raw))
                c['raw_has_targs'] += sum(map(lambda targ: int(bool(targ in repr(si.body.raw))), target_ids))
                c['raw_has_wp'] += int((si.body.raw is not None) and ('wikipedia.org' in si.body.raw))
                c['media_type'] += int(bool(si.body.media_type))
                c['clean_html'] += int(bool(si.body.clean_html))
                if si.body.clean_html:
                    c['clean_has_targs'] += sum(map(lambda targ: int(bool(targ in si.body.clean_html.decode('utf8'))), target_ids))
                    c['clean_has_wp'] += int(bool('wikipedia.org' in si.body.clean_html))

                c['clean_visible'] += int(bool(si.body.clean_visible))
                # c['labelsets'] += len(si.body.labelsets)  # TODO: broken? no such field ContentItem.labelsets
                #c['labels'] += sum(map(lambda labelset: len(labelset.labels), si.body.labelsets))
                c['labels'] += len(si.body.labels)
                label_targs = si.body.labels.keys()  # TODO: is this right? .values()
                #for labelset in si.body.labelsets:
                #    label_targs += [label.target_id for label in labelset.labels]
                c['labels_has_targs'] += sum(map(lambda targ: int(bool(targ in label_targs)), target_ids))
                _labels = collections.Counter()
                for sentences in si.body.sentences.values():
                    c['sentences'] += len(sentences)
                    for sent in sentences:
                        for tok in sent.tokens:
                            c['tokens'] += 1
                            for labell in tok.labels.itervalues():
                                for label in labell:
                                    _labels[label.annotator.annotator_id] += 1
                #print _labels
                labels += _labels
                c['at_least_one_label'] += int(bool(_labels))
                sys.stdout.flush()

        print fpath
        for k in keys:
            v = c.get(k)
            print '\t%s: %s' % (k, v)
        print '\tlabels: ' + ', '.join(['%s:%d' % it for it in labels.items()])
        #print json.dumps( c, indent=4 )
        #print json.dumps( labels, indent=4 )
        sys.stdout.flush()


def _copy(args):
    count = 0
    # TODO: separately set --out-version
    ochunk = Chunk(file_obj=sys.stdout, mode='wb')
    for fpath in args.input_path:
        ichunk = Chunk(path=fpath, mode='rb')
        for si in ichunk:
            count += 1
            ochunk.add(si)
            if (args.limit is not None) and (count >= args.limit):
                break
        ichunk.close()
        if (args.limit is not None) and (count >= args.limit):
            break
    ochunk.close()
    sys.stderr.write('wrote {0} items\n'.format(count))


def _slots_to_kv(ob):
    for sn in ob.__slots__:
        v = getattr(ob, sn)
        if v is not None:
            yield sn, to_primitives(v)

def _nonnullkvdict(ob):
    for k,v in ob.iteritems():
        if v is not None:
            yield k,v

def to_primitives(ob):
    '''convert most Python objects into primitives for JSON or CBOR

    Object must be acyclic! no loops!
    '''
    if ob is None:
        return ob
    if isinstance(ob, (str,unicode,int,long,float)):
        return ob
    if isinstance(ob, (tuple,list)):
        return [to_primitives(x) for x in ob]
    if isinstance(ob, dict):
        return {to_primitives(k):to_primitives(v) for k,v in _nonnullkvdict(ob)}
    if hasattr(ob, '__slots__'):
        return {sk:sv for sk,sv in _slots_to_kv(ob)}
    return {to_primitives(k):to_primitives(v) for k,v in _nonnullkvdict(ob.__dict__)}


def _to_cbor(args):
    count = 0
    ochunk = CborChunk(file_obj=sys.stdout, mode='wb', write_wrapper=to_primitives)
    for fpath in args.input_path:
        ichunk = Chunk(path=fpath, mode='rb')
        for si in ichunk:
            count += 1
            ochunk.add(si)
            if (args.limit is not None) and (count >= args.limit):
                break
        ichunk.close()
        if (args.limit is not None) and (count >= args.limit):
            break
    ochunk.close()
    sys.stderr.write('wrote {0} items\n'.format(count))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_path', 
        nargs='*',
        default=[],
        help='Paths to a chunk files, or directory of chunks, Note: "-" denotes stdin has a list of paths, NOT streamcorpus data')
    parser.add_argument('--stats', action='store_true', default=False,
                        help='print out the .body.raw of a specific stream_id')
    parser.add_argument('--tagger-stats', action='store_true', default=False,
                        help='Print the *relative* size of data contributed by each tagger.')
    parser.add_argument('--find', dest='find', metavar='STREAM_ID', help='print out the .body.raw of a specific stream_id')
    parser.add_argument('--binary', dest='dump_binary_stream_item', 
                        action='store_true', default=False, 
                        help='Use with --find to write full binary StreamItem of specific stream_id to stdout intead of .body.raw')
    parser.add_argument(
        '--find-missing', dest='find_missing', action='store_true', default=False,
        help='print out the .body.<content> of any stream_item that has no tokens with a label in annotator_ids')
    parser.add_argument(
        '--component', dest='component', metavar='raw|clean_html|clean_visible', 
        help='print out the .body.<component>')
    parser.add_argument('--version', default='v0_3_0')
    parser.add_argument('--tokens', action='store_true', 
                        default=False, dest='tokens')
    parser.add_argument('--ratings', action='store_true', default=False)
    parser.add_argument('--include-header', action='store_true', default=False, dest='include_header')
    parser.add_argument('--annotator_id', action='append', default=[],
                        dest='annotator_ids', help='only show tokens that have this annotator_id')
    parser.add_argument('--tagger_id', action='append', default=[],
                        dest='tagger_ids', help='only show tokens that have this tagger_id')
    parser.add_argument('--show-all', action='store_true', 
                        default=False, dest='show_all')
    parser.add_argument('--show-content-field', 
                        default=None, dest='show_content_field')
    parser.add_argument('--smart-dump', action='store_true',
                        default=False, dest='smart_dump')
    parser.add_argument('--len-field', 
                        action='append', 
                        default=[], dest='len_fields')
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
    parser.add_argument('--print-url', action='store_true',
                        default=False, dest='print_url')
    parser.add_argument('--copy', action='store_true', default=False, help='copy items to stdout, useful with --limit')
    if CborChunk.is_available:
        parser.add_argument('--to-cbor', action='store_true', default=False)
    parser.add_argument('--verbose', action='store_true', default=False)
    # TODO: there appears to be no way to have streamcorpus_dump
    # receive data on stdin. All of the subcommands want
    # paths. Several of the subcommands could easily have Chunk()
    # opening lifted and receive chunks instead of paths.
    #
    # parser.add_argument('--stdin', action='store_true', default=False)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.version not in versioned_classes:
        sys.exit('--version=%r is not in "%s"' \
                     % (args.version, '", "'.join(versioned_classes.keys())))

    global message_class
    message_class = versioned_classes[args.version]

    ## make input_path into an iterable over path strings
    paths = []
    for ipath in args.input_path:
        if ipath == '-':
            # read stdin as a list of paths
            paths.extend(itertools.imap(lambda line: line.strip(), sys.stdin))
        elif os.path.isdir(ipath):
            paths.extend(
                map(lambda fname: os.path.join(args.input_path, fname),
                    os.listdir(args.input_path)))
        else:
            paths.append(ipath)
    args.input_path = paths

    ## now actually do whatever was requested
    if args.fields:
        _show_fields(args.input_path, args.fields, args.len_fields)

    elif args.tagger_stats:
        _tagger_stats(args, args.input_path)

    elif args.stats:
        _stats(args.input_path)

    elif args.find:
        _find(args.input_path, args.find, 
              dump_binary_stream_item=args.dump_binary_stream_item)

    elif args.tokens:
        _dump_tokens(args.input_path, args.annotator_ids, args.tagger_ids)

    elif args.find_missing:
        _find_missing_labels(args.input_path, args.annotator_ids, args.component)

    elif args.verify_offsets:
        verify_offsets(args.input_path)

    elif args.ratings:
        _dump_ratings(args.input_path, 
                      annotator_ids=args.annotator_ids,
                      include_header=args.include_header)

    elif args.copy:
        _copy(args)

    elif args.to_cbor:
        _to_cbor(args)

    else:
        for fpath in args.input_path:
            _dump(fpath, args)


if __name__ == '__main__':
    main()
