#!/usr/bin/env python
'''
Example of how to read a streamcorpus.Chunk file add NLP metadata and
export a new Chunk file

A good practice is to use python virtualenv, so you can:

## setup your virtualenv
virtualenv --distribute ve
source ve/bin/activate

## install the latest development release of streamcorpus
pip install streamcorpus-dev

## fetch an example text file
wget http://nytimes.com

## tun this script
python example-streamcorpus-augmentor.py

'''
## "Chunk" is a convenience wrapper in the python tools built around
## the streamcorpus thirft interfaces.  It is essentially just a
## wrapper around open(<file_handle>) and can take a path to a flat
## file on disk, or a file_obj that has already been opened in memory,
## such as a pipe from stdin or a network socket.
from streamcorpus import Chunk

## This classes are available in any language that can compile the
## streamcorpus thrift interfaces
from streamcorpus import Tagging, Versions, Relation, Attribute, Sentence, Token

## read StreamItems from over stdin.  We will assume that these
## StreamItems have already been constructed and have
## StreamItem.body.clean_visible
i_chunk = Chunk(file_obj=sys.stdin, mode='rb')

## write StreamItems via stdout.  We will add more data to them
o_chunk = Chunk(file_obj=sys.stdout, mode='wb')

## iterate over input chunks, generate data, and write to output
for si in i_chunk:

    assert si.version == Versions.v0_3_0, 'new streamcorpus collections should be built using the latest version'

    ## clean_visible is byte identical to clean_html, except all the
    ## tags are converted to whitespace, so offsets in match
    #input_html = si.body.clean_html = text.encode('utf8')
    clean_visible = si.body.clean_visible.decode('utf8')

    ## run the text through a tagger
    #tagger_output = my_tagger( clean_visible )
    
    ## to illustrate, here, we construct a single sentence of tokens
    ## with all the fields populated
    first_sentence = Sentence()
    first_sentence.tokens = [
        Token(
            token='The',
            ),
        Token(
            token='cat',
            ),
        Token(
            token='jumped',
            ),
        Token(
            token='over',
            ),
        Token(
            token='the',
            ),
        Token(
            token='car',
            ),
        Token(
            token='.',
            ),
        ]

    ## store metadata about the tagger here:
    si.body.taggings['my_tagger_name'] = Taggings(
        tagger_id  = 'my_tagger_name', ## must match the key in the taggings map
        raw_tagging = '',  ## OPTIONAL, serialized tagging data in some "native" format
        tagger_config = 'streamcorpus-all.params',
        tagger_version = '6.0.1',
        generation_time = make_stream_time('2013-04-18T18:18:20.000000Z'),
        )

    
    si.body.sentences[tagger_id] = [Sentence(....) for ... in sentence_builder]

    ## now that you have populated this StreamItem, add it to the
    ## chunk file, and go to the next StreamItem
    ch.add(si)

    print 'added StreamItem.stream_id = %s from date_hour = %s' % (
        si.stream_id, get_date_hour(si))

## after adding all the StreamItems, close the chunk:
ch.close()

## Typically, chunk files should be limited to about 500 documents or
## smaller.  There are several nice pythonic techniques for making
## many chunk files, ask us for examples to suit your circumstances.

## Typically, all of the StreamItems in a chunk file have stream_times
## from the same hour in history.  That is, if you call
## get_date_hour(si) you should get the same string for every
## StreamItem in the chunk file.

## Organizing a large number of documents to meet these requirements
## can take some work.  Post an issue ticket if you want to discuss
## your needs.

print 'saved a file to %s with md5 sum: %s' % (output_path, ch.md5_hexdigest)
