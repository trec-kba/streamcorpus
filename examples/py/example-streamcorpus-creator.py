#!/usr/bin/env python
'''
Example of how to create streamcorpus.Chunk files using python

A good practice is to use python virtualenv, so you can:

## setup your virtualenv
virtualenv --distribute ve
source ve/bin/activate

## install the latest development release of streamcorpus
pip install streamcorpus-dev

## fetch an example text file
wget http://nytimes.com

## tun this script
python example-streamcorpus-creator.py

'''
from streamcorpus import make_stream_item, make_stream_time, Chunk, Tagging, Versions

## somehow get a list of input text files
# fake example with just one input, downloaded via wget (see __doc__
# string above)
input_files = ['index.html']

## open a chunk file to write StreamItems
output_path = 'first-output-chunk.sc'
ch = Chunk(output_path, mode='wb')

for file_path in input_files:

    ## get the text
    text = open(file_path).read()

    ## every StreamItem has a timestamp, which ideally is the creation
    ## time of the text
    zulu_timestamp = '2013-04-18T18:18:20.000000Z'

    ## every StreamItem has an absolute URL, which ideally points to
    ## the real text on the Web
    abs_url = 'http://nytimes.com/index.html'

    si = make_stream_item(zulu_timestamp, abs_url)

    assert si.version == Versions.v0_3_0, 'new streamcorpus collections should be built using the latest version'

    ## StreamItem.source must be a string without spaces that
    ## identifies the origin of the content.  Existing source names
    ## are 'social', 'news', 'linking', 'arxiv', 'FORUMS', and a few
    ## others.  Make up an appropriate source name for this content,
    ## it should be human readable and make sense as the name of the
    ## corpus.  Typically, when naming chunk files, we use
    ## "<date-hour>/<source>-<md5>.sc.xz"
    si.source = 'news'

    ## if the text is raw from the web and might contain control
    ## characters or have any encoding other than utf8, then put it in
    ## StreamItem.body.raw
    si.body.raw = text
    
    ## if the encoding is not specified, the pipeline might damage the
    ## text by guessing wrong, so it is important to put the correct
    ## encoding.
    si.body.encoding = 'UTF-8'

    si.body.media_type = 'text/html'  ## or 'text/plain'

    ## if the text is perfect HTML in utf8, then you can put it here,
    ## otherwise, the kba.pipeline will generate .clean_html from .raw
    #si.body.clean_html = text.encode('utf8')

    ## if the text is already free of HTML tags and is in utf8, then
    ## you can put it here:
    #si.body.clean_visible = text.encode('utf8')
    
    ## if you have existing XML from a tagger, e.g. Serif, you can put
    ## it here:
    #si.body.taggings['serif'] = Taggings(
    #    tagger_id = 'serif',
    #    raw_tagging = serifxml,
    #    tagger_config = 'streamcorpus-all.par',
    #    tagger_config = '6.0.1',
    #    generation_time = make_stream_time('2013-04-18T18:18:20.000000Z'),
    #    )

    ## To properly represent a taggers output in a StreamItem, you
    ## should populate these fields:
    #si.body.sentences[tagger_id] = [Sentence(....) for ... in sentence_builder]
    ## Serif can convert serifxml into this structure.

    ## now that you have populated this StreamItem, add it to the
    ## chunk file, and go to the next StreamItem
    ch.add(si)


## after adding all the StreamItems, close the chunk:
ch.close()

print 'saved a file to %s with md5 sum: %s' % (output_path, ch.md5_hexdigest)
