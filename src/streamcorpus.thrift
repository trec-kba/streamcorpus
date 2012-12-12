/**
 * These thrift definitions provide general structures for storing
 * collections of content.  It supports storing annotation metadata,
 * such as relevance judgments and labels, and also multiple
 * transformed editions of each document, such as after tag stripping,
 * parsing, and NER tagging.
 *
 * Change Log:
 *
 * December 2012: This more general version replaces kba.thrift file
 * used in TREC's Knowledge Base Acceleration evaluation in NIST's
 * TREC 2012 conference.  http://trec-kba.org
 *
 * This is released as open source software under the MIT X11 license:
 * Copyright (c) 2012 Computable Insights.
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
namespace java streamcorpus
namespace py streamcorpus

/**
 * StreamTime is a timestamp measured in seconds since the 1970 epoch.
 * epoch_ticks is always in the UTC timezone.  This is used in several
 * structs below to record various moments in history.
 */
struct StreamTime {
  1: double epoch_ticks,
  2: string zulu_timestamp,
}

/**
 * SourceMetadata is a binary object with format determined by
 * StreamItem.source.
 * 
 * For the kba-stream-corpus-2012, the SourceMetadata was always one
 * of these schemas where 'news', 'social', 'linking' is the string
 * found in CorpusItem.source
 *  - http://trec-kba.org/schemas/v1.0/news-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/linking-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/social-metadata.json
 *
 */
typedef binary SourceMetadata

/**
 * Offset and OffsetType are used by Annotation to identify the
 * portion of a ContentItem that a human labeled with a tag.
 */
enum OffsetType {
  // annotation applies to a range of line numbers
  LINES = 1,

  // annotation applies to a range of bytes
  BYTES = 2,

  // annotation applies to a range of chars
  CHARS = 3,
}

/*
 * Offset specifies a range within a field of data in this ContentItem
 */
struct Offset {
  // see above
  1: OffsetType type,

  // actual offset and length, which could be measured in bytes,
  // chars, or lines
  2: i32 first,
  3: i32 length,

  // if xpath is not empty, then annotation applies to an offset
  // within data that starts with an XPATH query into XHTML or XML
  4: optional string xpath,
}

/**
 * labels are human generated assertions about data.  For example, a
 * human author might label their own text by inserting hyperlinks to
 * Wikipedia, or a NIST assessor might record judgments about a TREC
 * document.
 */
struct Label {
  // a string describing the source, e.g. 'NIST TREC Assessor' or
  // 'Author Inserted Hyperlink'
  1: string annotator,

  // moment when annotation/judgment/label was rendered by human
  2: StreamTime label_time,

  // target_kb is a knowledge base of topics or entities used to
  // define the labels, e.g. http://en.wikipedia.org/wiki/ 
  3: string target_kb

  // moment in history that the target_kb was accessed
  4: StreamTime kb_snapshot_time,

  // string identifying the labeling target in the KB, e.g. a
  // 'urlname' in WP or an 'id' in Freebase.
  5: string target_id,

  // class instance hierarchy path to the data to which this labeling
  // applies.  This string will contain "." symbols, which imply
  // levels in the class instance hierarchy, e.g. 'body.ner' means
  // stream_item.body.ner.  If this attribute is empty, then the
  // label applies to the entire content item.
  6: optional string path,

  // pointer into the data identified by path
  7: optional Offset offset,

  // a numerical score with meaning that depends on the
  // label.annotator.  When used in IR rating, this might have a short
  // enumeration such as -1=Garbage, 0=Neutral, 1=Useful, 2=Vital
  8: optional i16 relevance,

  // another numerical score that is generally orthogonal to relevance
  // and also depends on the label.annotator
  9: optional i16 confidence,
}

/**
 * ContentItem contains raw data, an indication of its character
 * encoding, and various transformed versions of the raw data.
 *
 * 'cleansed' is generated from 'raw', and 'ner' is generated from
 * 'cleansed.'  Generally, 'cleansed' is a tag-stripped version of
 * 'raw', and 'ner' is the output of a named entity recognizer that
 * generates one-word-per-line output.
 *
 * For the kba-stream-corpus-2012, the specific tag-stripping and NER
 * configurations were:
 *   'raw' --> boilerpipe 1.2.0 KeepEverything --> 'cleansed'
 *
 *   'cleansed' -> Stanford CoreNLP ver 1.2.0 with annotators
 *        {tokenize, cleanxml, ssplit, pos, lemma, ner}, property
 *        pos.maxlen=100" --> 'ner'
 * 
 * For the kba-stream-corpus-2013, which includes all the same
 * original content as the 2012 corpus plus more, the tag stripping
 * and NER configs were:
 *
 * cleansed = strip_tags(raw, convert_common_entities=True, space_padding=True)
 * which inserts whitespace so that byte offsets into cleansed
 * correspond to the same positions in raw.
 *
 * ner = wrapper around Stanford CoreNLP v1.3.4 with annotators
 *        {tokenize, ssplit, pos, lemma, ner, parse, dcoref}
 *
 */
struct ContentItem {
  // original download, raw byte array
  1: binary raw, 
  
  // guessed from raw and/or headers, e.g. python requests library
  2: string encoding, 

  // all visible text, e.g. from boilerpipe 1.2.0 KeepEverything
  3: optional binary cleansed, 

  // One-Word-Per-Line (OWLP) tokenization and sentence chunking with
  // part-of-speech, lemmatization, and NER classification.
  4: optional binary ner, 

  // a set of annotations generated by humans
  5: optional list<Label> labels
}

/**
 * This is the primary interface to the corpus data.  It is called
 * StreamItem rather than CorpusItem and has a required StreamTime
 * attribute, because even for a static corpus, each document was
 * captured at a particular time in Earth history and might have been
 * different if captured earlier or later.  All corpora are stream
 * corpora, even if they were not explicitly created as such.
 *
 * stream_id is the unique identifier for documents in the corpus.
 * 
 */
struct StreamItem {
  // md5 hash of the abs_url
  1: string doc_id,  

  // normalized form of the original_url
  2: binary abs_url, 

  // scheme://hostname parsed from abs_url
  3: string schost,  

  // the original URL string obtain from some source
  4: binary original_url, 

  // string uniquely identifying this data set, generally should
  // include a year string
  5: string source,  

  // primary content
  6: ContentItem body,   

  // see above for explanation of the values that can appear in this
  // dictionary of metadata info from the source
  7: map<string, SourceMetadata> source_metadata, 

  // stream_id is actual unique identifier for the corpus,
  // stream_id = '%d-%s' % (int(stream_time.epoch_ticks), doc_id)
  8: string stream_id,  
  9: StreamTime stream_time,

  // other content items besides body, e.g. title, anchor
  10: optional map<string, ContentItem> other_content,  

  // A single anchor text of a URL pointing to this doc.  Note that
  // this does not have metadata like the URL of the page that
  // contained this anchor.  Such general link graph data may
  // eventually motivate an extension to this thrift definition.
}
