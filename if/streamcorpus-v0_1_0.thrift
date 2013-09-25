
/**
 * This was the first version of the KBA streamcorpus thrift format.
 * It has now been replaced by stramcorpus.thrift, which has version
 * numbers built into the structures.
 *
 * This set of thrift structures is analogous to the JSON schemas
 * defined in http://trec-kba.org/schemas/v1.0/
 * 
 * The comments below should be enough to interact with the text of
 * the corpus.  The JSON schemas contain additional details,
 * especially for the SourceMetadata, which is stored in the thrift as
 * a JSON string using the schemas linked below.
 */
namespace java streamcorpus
namespace py streamcorpus

/**
 * ContentItem is the thrift analog of
 * http://trec-kba.org/schemas/v1.0/content-item.json
 *
 * The JSON version has a 'stages' property that contains descriptions
 * **and also names** of additional properties on the ContentItem.
 * That was overly flexible.  Each content-item in the KBA corpus can
 * have a 'cleansed' and 'ner' property.  'cleansed' is generated from
 * 'raw', and 'ner' is generated from 'cleansed.'  Generally,
 * 'cleansed' is a tag-stripped version of 'raw', and 'ner' is the
 * output of a named entity recognizer that generates
 * one-word-per-line output.
 *
 * For the kba-stream-corpus-2012, the specific tag-stripping and NER
 * configurations were:
 *   'raw' --> boilerpipe 1.2.0 ArticleExtractor --> 'cleansed'
 *
 *   'cleansed' -> Stanford CoreNLP ver 1.2.0 with annotators
 *        {tokenize, cleanxml, ssplit, pos, lemma, ner}, property
 *        pos.maxlen=100" --> 'ner'
 */
struct ContentItem {
  1: binary raw,
  2: string encoding,
  3: optional binary cleansed,
  4: optional binary ner,
}

/**
 * SourceMetadata is a JSON string with one of these schemas
 *
 *  - http://trec-kba.org/schemas/v1.0/news-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/linking-metadata.json
 *  - http://trec-kba.org/schemas/v1.0/social-metadata.json
 *
 * where 'news', 'social', 'linking' is the string found in
 * CorpusItem.source
 *
 */
typedef binary SourceMetadata

/**
 * CorpusItem is the thrift equivalent of
 * http://trec-kba.org/schemas/v1.0/corpus-item.json
 */
struct CorpusItem {
  1: string doc_id,
  2: binary abs_url,
  3: string schost,
  4: binary original_url,
  5: string source,
  6: ContentItem title,
  7: ContentItem body,
  8: ContentItem anchor,
  9: SourceMetadata source_metadata,
}

/**
 * StreamTime is a timestamp measured in seconds since the 1970 epoch.
 * 'news', 'linking', and 'social' each have slightly different ways
 * of generating these timestamps.  See details:
 * http://trec-kba.org/kba-stream-corpus-2012.shtml
 */
struct StreamTime {
  1: double epoch_ticks,
  2: string zulu_timestamp,
}

/**
 * This is the primary interface to the data.  StreamItem is the
 * thrift equivalent of
 * http://trec-kba.org/schemas/v1.0/stream-item.json 
 * 
 * which extends corpus-item.json.  For better or worse, thrift does
 * not support inheritence on struct, so this copies the first nine
 * fields of CorpusItem and then adds two more fields.
 */
struct StreamItem {
  1: string doc_id,
  2: binary abs_url,
  3: string schost,
  4: binary original_url,
  5: string source,
  6: ContentItem title,
  7: ContentItem body,
  8: ContentItem anchor,
  9: SourceMetadata source_metadata,
  // stream_id is the actual unique identifier for the stream corpus,
  // stream_id = '%d-%s' % (int(stream_time.epoch_ticks), doc_id)
  10: string stream_id,  
  11: StreamTime stream_time,
}
