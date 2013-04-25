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
namespace cpp streamcorpus

/**
 * StreamTime is a timestamp measured in seconds since the 1970 epoch.
 * epoch_ticks is always in the UTC timezone.  This is used in several
 * structs below to record various moments in history.
 *
 * Implementations of these interfaces in various languages may
 * provide convenience methods for insuring that these two fields are
 * consistent with each other.
 */
struct StreamTime {
  1: double epoch_ticks,
  2: string zulu_timestamp,
}

/**
 * AnnotatorID is used as a property in Annotator structs and also as
 * a key on maps in ContentItem.
 *
 * It is just a string.  There is no enum for it, so consistency and
 * uniqueness depends on the system generating the AnnotatorID.
 *
 * AnnotatorID identifies the source of a Label or Rating object.  It
 * is not necessarily unique.  We use these conventions:
 *
 *  - Avoid whitespace.  
 *
 *  - email address is the best identifier
 *
 *  - when a single email address is not appropriate, create a
 *    descriptive string, e.g. 'nist-trec-kba-2012-assessors'
 *
 *  - 'author' means the person who wrote the original text
 */
typedef string AnnotatorID

/**
 * An Annotator object describes a human (or possibly a set of humans)
 * who generated the data stored in a Label or Rating object.
 */
struct Annotator {
  1: AnnotatorID annotator_id,

  /**
   * Approximate time when annotations/judgments/labels was rendered
   * by human.  If this is missing, it means that the time was not
   * recorded, which often happens when the author made the
   * annotation.
   */
  2: optional StreamTime annotation_time,
}

/**
 * Offset and OffsetType are used by Annotation to identify the
 * portion of a ContentItem that a human labeled with a tag.
 *
 * annotation applies to a range of line numbers
 *
 * annotation applies to a range of bytes
 *
 * annotation applies to a range of chars, typically unicode chars
 */
enum OffsetType {
  LINES = 0,

  BYTES = 1,

  CHARS = 2,
}

/**
 * Offset specifies a range within a field of data in this ContentItem
 */
struct Offset {
  /**
   * see comments on OffsetType
   */
  1: OffsetType type,

  /**
   * actual offset, which could be measured in bytes, chars, or lines.
   * The data element identified by 'first' is included, and that
   * identified by first+length is also included.
   *
   * In set notation, 
   *     [first:first+length-1]
   *
   * or equivalently
   *     [first:first+length)
   *
   * or in list slicing, like python's:
   *     [first:first+length]
   *
   * While thrift treats these as signed integers, negative values are
   * meaningless in this context, i.e. we do not end wrap.
   */
  2: i64 first,
  3: i32 length,

  /**
   * if xpath is not empty, then annotation applies to an offset
   * within data that starts with an XPATH query into XHTML or XML
   */
  4: optional string xpath,

  /**
   * name of the data element inside a ContentItem to which this label
   * applies, e.g. 'raw' 'clean_html' or 'clean_visible'.  Defaults to
   * clean_visible, which is the most common case.
   */
  5: optional string content_form = "clean_visible",

  /**
   * bytes specified by this offset extracted from the original; just
   * to assist in debugging
   */
  6: optional binary value,
}

/**
 * Targets are "informationt targets," such as entities or topics,
 * usually from a knowledge base, such as Wikipedia.
 */
struct Target {
  /**
   * unique string identifier, usually a URL into Wikipedia, Freebase,
   * or some other structured reference system for info targets.  
   */
  1: string target_id,

  /**
   * kb_id is usually redundant if the target_id is a full URL,
   * e.g. en.wikipedia.org
   */
  2: optional string kb_id,

  /**
   * moment in history that the target_kb was accessed
   */
  3: optional StreamTime kb_snapshot_time,
}

/**
 * Labels are human generated assertions about a portion of a document
 * For example, a human author might label their own text by inserting
 * hyperlinks to Wikipedia, or a NIST assessor might record which
 * tokens in a text mention a target entity.
 * 
 * Label instances can be attached in three palces:
 *  -  Token.labels  list
 *  -  Sentence.labels  list
 *  -  ContentItem.labels  map
 */
struct Label {
  /**
   * identifies the source of this Label
   */
  1: Annotator annotator,

  /**
   * identifies the information need assessed by annotator
   */
  2: Target target,

  /**
   * pointers to data to which this label applies.  If empty, then
   * label applies to the entire Token, Sentence, or ContentItem to
   * which it is attached.
   */
  3: optional map<OffsetType, Offset> offsets = {},
}

/**
 * Different tagging tools have different strings for labeling the
 * various common entity types.  To avoid ambiguity, we define a
 * canonical list here, which we will surely have to expand over time
 * as new taggers recognize new types of entities.
 *
 * LOC: physical location
 *
 * MISC: uncategorized named entities, e.g. Civil War for Stanford CoreNLP
 */
enum EntityType {
  PER = 0,
  ORG = 1,
  LOC = 2,
  MALE_PRONOUN = 3, // necessary but crufty
  FEMALE_PRONOUN = 4, // necessary but crufty
  TIME = 5,
  DATE = 6,
  MONEY = 7,
  PERCENT = 8,

  MISC = 9, 

  GPE = 10,
  FAC = 11,
  VEH = 12,
  WEA = 13,
  phone = 14,
  email = 15,
  URL = 16,
}

/**
 * mention_id are i16 and unique only within a sentence
 */
typedef i16 MentionID

/**
 * Textual tokens identified by an NLP pipeline and marked up with
 * metadata from automatic taggers and possibly also Labels from
 * humans.
 */
struct Token {
  /**
   * zero-based index into the stream of tokens from a document
   */
  1: i32 token_num,

  /**
   * actual token string, must always be a UTF8 encoded string, not a
   * unicode string, because thrift stores them as 8-bit.
   */
  2: string token,

  /**
   * offsets into the original data (see Offset.content_form)
   */
  3: optional map<OffsetType, Offset> offsets = {},

  /**
   * zero-based index into the sentence, which is used for dependency
   * parsed data
   */
  4: optional i32 sentence_pos = -1,

  /**
   * lemmatization of the token, again must be UTF8
   */
  5: optional string lemma,

  /**
   * part of speech labels defined by Penn TreeBank:
   * http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
   * Should probably convert this to an enum, analogous to EntityType
   */
  6: optional string pos,

  /**
   * entity type from named entity recognizer (classifier)
   */
  7: optional EntityType entity_type,

  /**
   * Identifier for a each mention in a sentence.  Must be zero-based
   * within each sentence, so is not unique at the document level.
   * Serves two purposes:
   *
   *   1) Distinguishing multi-token mention.  Needed when the
   *   entity_type and equiv_id do not change between tokens that are
   *   part of separate mentions, e.g. "The senator is known to his
   *   friends as David, Davy, Zeus, and Mr. Elephant."
   *
   *   2) Refering to mentions used in Relation objects.  Used in
   *   conjunction with sentence_id
   */
  8: optional MentionID mention_id = -1,

  /**
   * Within-doc coref chain ID.  That is, identifier of equivalence
   * class of co-referent tokens.  Default is -1, meaning None.
   */
  9: optional i32 equiv_id = -1,

  /**
   * parent sentence_pos in dependency parse. Default is -1, ie None
   */
  10: optional i32 parent_id = -1,

  /**
   * grammatical relation label on path to parent in dependency parse,
   * defined by whatever tagger was used -- should pick a canonical
   * definition here and convert it to an enum.
   */
  11: optional string dependency_path,

  /** 
   * Labels attached to this token, defaults to an empty map
   */
  12: optional map<AnnotatorID, list<Label>> labels = {},
}

struct Sentence {
  /**
   * tokens in this sentence
   */
  1: list<Token> tokens = [],

  /**
   * array of instances of Label attached to this sentence, defaults to
   * an empty map
   */
  2: optional map<AnnotatorID, list<Label>> labels = {},
}

/**
 * TaggerID is used as a key on maps in ContentItem.  
 *
 * It is just a string.  There is no enum for it, so consistency and
 * uniqueness depends on the system generating the TaggerID.
 */
typedef string TaggerID

struct Tagging {
  1: TaggerID tagger_id,

  /**
   * raw output of the tagging tool
   */
  2: binary raw_tagging,

  /**
   * short human-readable description of configuration parameters
   */
  3: optional string tagger_config,

  /**
   * short human-readable version string of the tagging tool
   */
  4: optional string tagger_version,

  /**
   * time that tagging was generated
   */
  5: optional StreamTime generation_time,
}

/**
 * Description of a relation between two entities that a tagger
 * discovered in the text.
 */
struct Relation {
  /**
   * A string describing the relation.  We may convert these to an
   * enumeration, which would then be called relation_type
   *
   * Here is a list of ACE relation (and event) types that might
   * appear in relation_name
   * http://projects.ldc.upenn.edu/ace/docs/English-Events-Guidelines_v5.4.3.pdf

PHYS.Located
PHYS.Near
PART-WHOLE.Geographical
PART-WHOLE.Subsidiary
PART-WHOLE.Artifact
PER-SOC.Business
PER-SOC.Family
PER-SOC.Lasting-Personal
ORG-AFF.Employment
ORG-AFF.Ownership
ORG-AFF.Founder
ORG-AFF.Student-Alum
ORG-AFF.Sports-Affiliation
ORG-AFF.Investor-Shareholder
ORG-AFF.Membership
ART.User-Owner-Inventor-Manufacturer
GEN-AFF.Citizen-Resident-Religion-Ethnicity
GEN-AFF.Org-Location


Business.Declare-Bankruptcy
Business.End-Org
Business.Merge-Org
Business.Start-Org
Conflict.Attack
Conflict.Demonstrate
Contact.Phone-Write
Contact.Meet
Justice.Acquit
Justice.Appeal
Justice.Arrest-Jail
Justice.Charge-Indict
Justice.Convict
Justice.Execute
Justice.Extradite
Justice.Fine
Justice.Pardon
Justice.Release-Parole
Justice.Sentence
Justice.Sue
Justice.Trial-Hearing
Life.Be-Born
Life.Die
Life.Divorce
Life.Injure
Life.Marry
Movement.Transport
Personnel.Elect
Personnel.End-Position
Personnel.Nominate
Personnel.Start-Position
Transaction.Transfer-Money
Transaction.Transfer-Ownership

   */
  1: optional string relation_name,

  /**
   * Zero-based index into the sentences array for this TaggerID
   */
  2: optional i32 sentence_id_1,

  /**
   * Zero-based index into the mentions in that sentence.  This
   * identifies the origin of the relation.  For example, the relation
   *    (Bob, PHYS.Located, Chicago)
   * would have mention_id_1 point to Bob.
   */
  3: optional MentionID mention_id_1,

  /**
   * Zero-based index into the sentences array for this TaggerID
   */
  4: optional i32 sentence_id_2,

  /**
   * Zero-based index into the mentions in that sentence. This
   * identifies the origin of the relation.  For example, the relation
   *    (Bob, PHYS.Located, Chicago)
   * would have mention_id_2 point to Chicago.
   */
  5: optional MentionID mention_id_2,

  // could add equiv_id_1 and equiv_id_2
}

/**
 * Description of a natural language used in text
 */
struct Language {
  /**
   * two letter code for the language
   */
  1: string code = "",
  2: optional string name = "", 
}

/**
 * ContentItem contains raw data, an indication of its character
 * encoding, and various transformed versions of the raw data.
 */
struct ContentItem {
  /**
   * original download, raw byte array
   */
  1: optional binary raw, 
  
  /**
   * guessed from raw and/or headers, e.g. by python-requests.org
   */
  2: optional string encoding, 

  /**
   * Content-type header from fetching the data, or MIME type
   */
  3: optional string media_type,

  /**
   * HTML-formatted version of raw with UTF8 encoding and no broken
   * tags.  All HTML-escaped characters are converted to their UTF8
   * equivalents.  < > & are escaped.
   */
  4: optional string clean_html,

  /**
   * All tags stripped from clean_html and replaced with whitespace,
   * so they have the same byte offsets.  The only escaped characters
   * are < > &, so that this can be treated as Character Data in XML:
   * http://www.w3.org/TR/xml/#syntax
   *
   * Again: must be UTF8
   */
  5: optional string clean_visible, 

  /**
   * Logs generated from processing pipeline, for forensics
   */
  6: optional list<string> logs = [],

  /**
   * A set of auto-generated taggings, such as a One-Word-Per-Line
   * (OWLP) tokenization and sentence chunking with part-of-speech,
   * lemmatization, and NER classification.  The string name should be
   * the same as the tagger_id and also corresponds to the key in
   * sentences or sentence_blobs, which get generated by transforming
   * a Tagging.raw_tagging into Sentence and Token instances
   *
   * Taggings are generated from 'clean_visible' so offsets (byte,
   * char, line) refer to clean_visible and clean_html -- not raw.
   */
  7: optional map<TaggerID, Tagging> taggings = {}, 

  /**
   * sets of annotations
   */
  8: optional map<AnnotatorID, list<Label>> labels = {},

  /**
   * parsed Sentence objects generated by an NLP pipeline identified
   * by the string name, which is a tagger_id that connects this
   * Sentences instance to the Tagging struct from which it came
   */
  9: optional map<TaggerID, list<Sentence>> sentences = {},

  /**
   * same as 'sentences' except the array of Sentence instances are
   * serialized into a binary string that can be read by the Thrift's
   * binary protocol.  This allows lazy deserialization via an
   * iterator -- one sentence at a time.  This might be totally
   * unnecessary, because at least some of the Thrift language
   * implementations have lazy object construction, e.g. --gen
   * py:dynamic,slots
   */
  10: optional map<TaggerID, binary> sentence_blobs = {},

  /**
   * indication of which natural language is used in the text
   */
  11: optional Language language,

  /**
   * List of relations discovered in clean_visible
   */
  12: optional map<TaggerID, list<Relation>> relations = {},
}

/**
 * Ratings are buman generated assertions about a entire document's
 * utility for a particular topic or entity in a reference KB.
 */
struct Rating {
  /**
   * identifies the source of this Rating
   */
  1: Annotator annotator,

  /**
   * identifies the information need assessed by annotator
   */
  2: Target target,

  /**
   * numerical score assigned by annotator to "judge" or "rate" the
   * utility of this StreamItem to addressing the target information
   * need.  The range and interpretation of relevance numbers depends
   * on the annotator.  relevance can represent a rank ordering or an
   * enumeration such as -1=Garbage, 0=Neutral, 1=Useful, 2=Vital
   */
  3: optional i16 relevance,

  /** 
   * true|false indication of whether the document mentions the target
   * entity.  This is only partially correlated with relevance.  For
   * example, a document might mention the entity only in chrome text
   * on the side such that it is a Garbage-rated text for that entity.
   */
  4: optional bool contains_mention,

  /**
   * Save notes from Annotator about this Rating
   */
  5: optional string comments,


  /**
   * Record strings that are "mentions" of the target in this text
   */
  6: optional list<string> mentions,
}

/**
 * SourceMetadata is a binary object with format determined by the key
 * in StreamItem.source_metadata, which is often the same as
 * StreamItem.source.
 * 
 * For the kba-stream-corpus-2012, the SourceMetadata was always one
 * of these schemas where 'news', 'social', 'linking' is the string
 * found in StreamItem.source and the source_metadata map's key:
 *  - http://trec-kba.org/schemas/v1.0/news-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/linking-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/social-metadata.json
 *
 * Other keys in the source_metadata map can be:
 *
 *  - http_headers
 */
typedef binary SourceMetadata

/**
 * Versions of this protocol are enumerated so that when we expand,
 * everybody can see which version a particular data file used.
 *
 * v0_1_0 refers to the kba.thrift definition, which was before
 * Versions was included in the spec.
 */
enum Versions {
  v0_2_0 = 0,
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
 * This is similar to the StreamItem defined in kba.thrift for TREC
 * KBA 2012, however it removes the 'title' and 'anchor' fields, which
 * can now be represented in other_content.  This means that code that
 * was written to read messages from kba.thrift must be updated.
 */
struct StreamItem {
  /**
   * must provide a version number here
   */
  1: Versions version = 0,

  /**
   * md5 hash of the abs_url
   */
  2: string doc_id,  

  /**
   * normalized form of the original_url, should be a valid URL
   */
  3: optional binary abs_url, 

  /**
   * scheme://hostname parsed from abs_url
   */
  4: optional string schost,  

  /**
   * string obtain from some source.  Only present if not a valid URL,
   * in which case abs_url was derived from original_url
   */
  5: optional binary original_url, 

  /**
   * string uniquely identifying this data set, should start with a
   * year string, such as 'news' or 'social'
   */
  6: optional string source,

  /**
   * primary content
   */
  7: optional ContentItem body,

  /**
   * see above for explanation of the values that can appear in this
   * dictionary of metadata info from the source.  The string keys in
   * this map should be short, descriptive, and free of whitespace.
   */
  8: optional map<string, SourceMetadata> source_metadata = {}, 

  /**
   * stream_id is actual unique identifier for a StreamItem.  The
   * format is:
   *
   * stream_id = '%d-%s' % (int(stream_time.epoch_ticks), doc_id)
   */
  9: string stream_id,

  /** 
   * earliest time that this content was known to exist.  Usually,
   * body.raw was also saved at the time of that first observation.
   */
  10: StreamTime stream_time,

  /**
   * such as title, anchor, extracted, etc.  When present, 'anchor',
   * is a single anchor text of a URL pointing to this doc.  Note that
   * this does not have metadata like the URL of the page that
   * contained this anchor.  Such general link graph data may
   * eventually motivate an extension to this thrift interface.
   */
  11: optional map<string, ContentItem> other_content = {},

  /**
   * doc-level judgments relating entire StreamItem to a Target
   */
  12: optional map<AnnotatorID, list<Rating>> ratings = {},
}
