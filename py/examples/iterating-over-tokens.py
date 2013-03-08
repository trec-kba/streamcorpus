'''
Example of using the python streamcorpus library to iterate over
documents and then iterate over tokens.  The output of this example is
a sequence of labels for tokens.
'''
## import that python module that wraps the streamcorpus.thrift
## interfaces.  We will only use the Chunk convenience interface,
## which reads StreamItem messages out of flat files.
import streamcorpus

## use sys module to access commandline arguments
import sys


## iterate over StreamItem messages in a flat file
for si in streamcorpus.Chunk(path=sys.argv[1]):

    ## iterate over the sentences map
    for tagger_id in si.body.sentences:
        for sentence in si.body.sentences[tagger_id]:

            ## iterate over the tokens in each sentence
            for token in sentence.tokens:

                ## iterate over the labels map
                for annotator_id in token.labels:
                    for label in token.labels[annotator_id]:

                        ## print the target_id for each label
                        print label.target.target_id
