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
 * Other types of SourceMetadata include:
 *  - http_headers
 */
typedef binary SourceMetadata

/**
 * An Annotator object describes a human (or possibly a set of humans)
 * who generated the data stored in a Label or Rating object.
 */
struct Annotator {
  // annotator_id is a tring that identifies the source, possibly
  // somewhat uniquely.  Avoid whitespace.  We use these conventions:
  //
  //    * email address is the best identifier
  //
  //    * when a single email address is not appropriate, create a
  //    * descriptive string, e.g. nist-trec-kba-2012-assessors
  //
  //    * 'author' means the person who wrote the original text
  1: string annotator_id,

  // Approximate time when annotations/judgments/labels was rendered
  // by human.  If this is missing, it means that the time was not
  // recorded, which often happens when the author made the
  // annotation.
  2: optional StreamTime annotation_time,

  // target_kb is a knowledge base of topics or entities used to
  // define the labels, e.g. http://en.wikipedia.org/wiki/ 
  3: optional string reference_kb,

  // moment in history that the target_kb was accessed
  4: optional StreamTime kb_snapshot_time,
}

/**
 * Offset and OffsetType are used by Annotation to identify the
 * portion of a ContentItem that a human labeled with a tag.
 */
enum OffsetType {
  // annotation applies to a range of line numbers
  LINES = 1,

  // annotation applies to a range of bytes
  BYTES = 2,

  // annotation applies to a range of chars, typically unicode chars
  CHARS = 3,
}

/*
 * Offset specifies a range within a field of data in this ContentItem
 */
struct Offset {
  // see above
  1: OffsetType type,

  // actual offset, which could be measured in bytes, chars, or lines.
  // The data element identified by 'first' is included, and that
  // identified by first+length is also included.
  //
  // In set notation, 
  //     [first:first+length]
  //
  // or equivalently
  //     [first:first+length+1)
  //
  // While thrift treats these as signed integers, negative values are
  // meaningless in this context, i.e. we do not end wrap.
  2: i64 first,
  3: i32 length,

  // if xpath is not empty, then annotation applies to an offset
  // within data that starts with an XPATH query into XHTML or XML
  4: optional string xpath,

  // name of the data element inside a ContentItem to which this label
  // applies, e.g. 'raw' 'cleansed' or 'ner'.  For example, 'ner'
  // means stream_item.<THIS_CONTENT_ITEM>.ner.  If missing, then this
  // offset should be part of a Token.
  5: optional string content_form,
}

/**
 * Labels are human generated assertions about a portion of a document
 * For example, a human author might label their own text by inserting
 * hyperlinks to Wikipedia, or a NIST assessor might record which
 * tokens in a text mention a target entity.
 * 
 * Label instances can be attached to an individual Token and
 * Sentence, or in a LabelSet.labels describing multiple parts of a
 * piece of data in a ContentItem.
 */
struct Label {
  // string identifying the labeling target in the KB, e.g. a
  // 'urlname' in WP or an 'id' in Freebase.
  1: string target_id,

  // Pointer to data to which this label applies.  If missing, then
  // label is either attached to a single Token or Sentence or
  // ContentItem, and applies to the entire thing.
  2: optional Offset offset,

  // description of person who asserted this rating.  If missing, then
  // this label should be part of a LabelSet that provides an
  // Annotator.
  3: optional Annotator annotator,
}

struct LabelSet {
  // description of person who asserted this rating.
  1: Annotator annotator,

  // a set of several labels
  2: list<Label> labels,
}

/**
 * Textual tokens identified by an NLP pipeline and marked up with
 * metadata from automatic taggers and possibly also Labels from
 * humans.
 */
struct Token {
  // zero-based index into the stream of tokens from a document
  1: i16 token_number,

  // actual token string
  2: binary token,

  // offset into the original data, typically 'cleansed'
  3: optional Offset offset,

  // zero-basd index into the sentence, which is used for dependency
  // parsed data
  4: optional i16 sentence_position = -1,

  // lemmatization of the token
  5: optional binary lemma,

  // part of speech labels defined by Penn TreeBank:
  // http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
  6: optional string pos,

  // entity type from named entity recognizer (classifier)
  7: optional string entity_type,

  // parent sentence_position in dependency parse.  Default is -1, meaning None.
  8: optional i16 parent_id = -1,

  // grammatical relation label on path to parent in dependency parse,
  // defined by whatever tagger was used.
  9: optional string dependency_path,

  // Within-doc coref chain ID.  That is, identifier of equivalence
  // class of co-referent tokens.  Default is -1, meaning None.
  10: optional i16 equivalence_id = -1,

  // array of instances of Label attached to this token, defaults to
  // an empty list
  11: optional list<Label> labels = [],
}

struct Sentence {
  // tokens in this sentence
  1: list<Token> tokens,

  // array of instances of Label attached to this sentence, defaults to
  // an empty list
  2: optional list<Label> labels = [],
}

struct Tagging {
  // short string identifying the tagger type, e.g. stanford-corenlp
  // or lingpipe
  1: string tagger_id,

  // raw output of the tagging tool
  2: binary raw_tagging,

  // short human-readable description of configuration parameters
  3: optional string tagger_config,

  // short human-readable version string of the tagging tool
  4: optional string tagger_version,

  // time that tagging was generated
  5: optional StreamTime generation_time,
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
  
  // guessed from raw and/or headers, e.g. by python-requests.org
  2: string encoding, 

  // all visible text with same byte offsets as raw, created by
  // streamcorpus.strip_tags
  3: optional binary cleansed, 

  // A set of auto-generated taggings, such as a One-Word-Per-Line
  // (OWLP) tokenization and sentence chunking with part-of-speech,
  // lemmatization, and NER classification.  The string name should be
  // the same as the tagger_id and also corresponds to the key in
  // sentences or sentence_blobs, which get generated by transforming
  // a Tagging.raw_tagging into Sentence and Token instances
  4: optional map<string, Tagging> taggings = {}, 

  // a set of annotations with names (the string in the map is the name)
  5: optional map<string, LabelSet> labelsets = {},

  // parsed Sentence objects generated by an NLP pipeline identified
  // by the string name
  6: optional map<string, list<Sentence>> sentences = {},

  // same as 'sentences' except the array of Sentence instances are
  // serialized into a binary string that can be read by the Thrift's
  // binary protocol.  This allows lazy deserialization via an
  // iterator -- one sentence at a time.
  7: optional map<string, binary> sentence_blobs = {},
}

/**
 * Ratings are buman generated assertions about a entire document's
 * utility for a particular topic or entity in a reference KB.
 */
struct Rating {
  // description of person who asserted this rating
  1: Annotator annotator,

  // 'urlname' in WP or an 'id' in Freebase.
  2: string target_id,

  // relevance is a numerical score with meaning that depends on the
  // Rating.annotator.  This can represent a rank ordering or a short
  // enumeration such as -1=Garbage, 0=Neutral, 1=Useful, 2=Vital
  3: optional i16 relevance,

  // mentions is a true|false indication of whether the document
  // mentions the target entity.  This is only partially correlated
  // with the rating.  For example, a document might mention the
  // entity only in chrome text on the side such that it is a
  // Garbage-rated text for that entity.
  4: optional bool mentions,
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
 * This is mostly the same as the StreamItem defined in kba.thrift for
 * TREC KBA 2012, however it removes the 'title' and 'anchor' fields,
 * which can now be represented in other_content.  This means that
 * code that was written to read messages from kba.thrift must be
 * updated.
 */
struct StreamItem {
  // md5 hash of the abs_url
  1: string doc_id,  

  // normalized form of the original_url
  2: optional binary abs_url, 

  // scheme://hostname parsed from abs_url
  3: optional string schost,  

  // the original URL string obtain from some source
  4: optional binary original_url, 

  // string uniquely identifying this data set, should start with a
  // year string, such as 2012-trec-kba-news or 2012-trec-kba-social
  5: optional string source,  

  // primary content
  6: optional ContentItem body,

  // see above for explanation of the values that can appear in this
  // dictionary of metadata info from the source.  The string names in
  // this map should be short, descriptive, and free of whitespace.
  7: optional map<string, SourceMetadata> source_metadata = {}, 

  // stream_id is actual unique identifier for the corpus.  
  //
  //    Standard format is:
  // stream_id = '%d-%s' % (int(stream_time.epoch_ticks), doc_id)
  8: string stream_id,

  // The earliest time that this content was known to exist.  In most
  // cases, it was also saved into this format at the time of that
  // first observation.
  9: StreamTime stream_time,

  // other content items besides body, e.g. title, anchor
  10: optional map<string, ContentItem> other_content = {},

  // When present, 'anchor', is a single anchor text of a URL pointing
  // to this doc.  Note that this does not have metadata like the URL
  // of the page that contained this anchor.  Such general link graph
  // data may eventually motivate an extension to this thrift
  // definition.

  // Document-level ratings that relate this entire StreamItem to a
  // topic or entity
  11: optional list<Rating> ratings = [],
}
