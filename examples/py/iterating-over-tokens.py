'''
Example of using the python streamcorpus library to iterate over
documents and then iterate over tokens.  The output of this example is
a sequence of labels for tokens.

This serves as documentation for both the Thrift message structures in
streamcorpus v0_2_0, and also the data in the KBA 2013 corpus:

 https://github.com/trec-kba/streamcorpus/blob/master/if/streamcorpus.thrift

 http://s3.amazonaws.com/aws-publicdatasets/trec/kba/index.html


For example, you can run this like this:

python  iterating-over-tokens.py  ../../test-data/john-smith-tagged-by-lingpipe-0.sc

or, you can try a Chunk from the KBA 2013 streamcorpus:

## download a chunk from the KBA 2013 corpus
  wget http://s3.amazonaws.com/aws-publicdatasets/trec/kba/kba-streamcorpus-2013-v0_2_0-english-and-unknown-language/2012-11-07-18/MAINSTREAM_NEWS-393-839f04b6bd4e90a5f284c91c43d58b60-f2ed7aa60c5e2999de9585c982756edd.sc.xz.gpg

## decrypt with key from NIST
  gpg MAINSTREAM_NEWS-393-839f04b6bd4e90a5f284c91c43d58b60-f2ed7aa60c5e2999de9585c982756edd.sc.xz.gpg > MAINSTREAM_NEWS-393-839f04b6bd4e90a5f284c91c43d58b60-f2ed7aa60c5e2999de9585c982756edd.sc.xz

## run this program on it
  python iterating-over-tokens.py  MAINSTREAM_NEWS-349-e471e2725727236219a831a277f72295-d2a1a49a5216d3383bd1e401233028a5.sc.xz

'''
## import that python module that wraps the streamcorpus.thrift
## interfaces.  We will only use the Chunk convenience interface,
## which reads StreamItem messages out of flat files.
import streamcorpus

## use sys module to access commandline arguments
import sys


## iterate over StreamItem messages in a flat file
### In other languages, you may need to create a read loop like this:
### https://github.com/trec-kba/streamcorpus/blob/master/java/src/test/ReadThrift.java
for si in streamcorpus.Chunk(path=sys.argv[1]):

    ## iterate over the sentences map for each tagger.
    #
    # taggers are identified by tagger_id strings, e.g. 'lingpipe' or 'serif' or 'stanford'
    #
    for tagger_id in si.body.sentences:
        for sentence in si.body.sentences[tagger_id]:

            ## iterate over the tokens in each sentence
            for token in sentence.tokens:

                ## iterate over the labels map
                target_ids = []
                for annotator_id in token.labels:
                    for label in token.labels[annotator_id]:

                        ## print the target_id for each label
                        target_ids.append( label.target.target_id )


                ## token has many useful properties:
                #
                # token.token is the word itself
                # 
                # token.mention_id is a number that distinguishes
                # multi-token named entity mentions
                # 
                # token.equiv_id is a number that identifies
                # within-doc coref chains of mentions to the same
                # entity
                # 
                # token.entity_type is the type of the entity
                if token.entity_type is not None:
                    ## we could just display the integer of the
                    ## token.entity_type, however it is easier to read
                    ## if we pull the name out of the EntityType
                    ## enumeration:
                    entity_type_name = streamcorpus.EntityType._VALUES_TO_NAMES[token.entity_type]
                else:
                    entity_type_name = '   '


                print '\t'.join(map(str, [token.mention_id, token.equiv_id, entity_type_name, token.token, target_ids]))

                ## In some corpora, e.g. the KBA 2013 corpus, the
                ## target_id is a full URL, such as the URL used by
                ## the author of the HTML from the text was extracted.

                ## In most corpora, the StreamItem.body.clean_html
                ## contains a properly structured version UTF-8 of the
                ## original HTML in StreamItem.body.raw The
                ## clean_visible is constructed from clean_html by
                ## replacing all bytes that are part of HTML tags with
                ## ' ', so that the byte offsets remain the same.
                ## This allowed us construct hyperlink_labels for the
                ## tokens.

    ## some documents have NER data stored only as raw_tagging output
    ## and have not be unpacked into thrift structures.  Specifically,
    ## the NER data from KBA 2012 has been preserved in the KBA 2013
    ## streamcorpus here:
    #StreamItem.body.taggings['stanford'].raw_tagging
                
    print

    if si.body.clean_visible:
        num_bytes = len(si.body.clean_visible)
        num_chars = len(si.body.clean_visible.decode('UTF-8'))
        print '%d bytes %d characters in StreamItem(%r).body.clean_visible for %s' % (num_bytes, num_chars, si.stream_id, si.abs_url)

    print '-------'

