#include <inttypes.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <iostream>
#include <cstdio>
#include <time.h>
#include <boost/unordered_map.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <fstream>

#include "streamcorpus_types.h"
#include "streamcorpus_constants.h"

#include <protocol/TBinaryProtocol.h>
#include <protocol/TDenseProtocol.h>
#include <protocol/TJSONProtocol.h>
#include <transport/TTransportUtils.h>
#include <transport/TFDTransport.h>
#include <transport/TFileTransport.h>

#include <boost/filesystem.hpp>
#include <boost/filesystem/path.hpp>
#include <boost/program_options.hpp>

using namespace std;
using namespace boost;
using namespace boost::filesystem;
using namespace apache::thrift;
using namespace apache::thrift::protocol;
using namespace apache::thrift::transport;

namespace po = boost::program_options;

using namespace streamcorpus;

int main(int argc, char **argv) {

    clog << "Starting program" <<endl;
    
    string text_source("clean_visible");

    bool negate(false);

    // Supported options.
    po::options_description desc("Allowed options");
    desc.add_options()
    ("help,h", "help message")
    ("text_source,t", po::value<string>(&text_source), "text source in stream item")
    ("negate,n", po::value<bool>(&negate)->implicit_value(true), "negate sense of match")
    ;

    // Parse command line options
    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    if (vm.count("help")) {
        cout << desc << "\n";
        return 1;
    }

    // Create annotator object
    Annotator annotator;
    AnnotatorID annotatorID;
    annotatorID = "example-matcher-v0.1";

    // Annotator identifier
    annotator.annotator_id = "example-matcher-v0.1";

    // Time this annotator was started
    StreamTime streamtime;
    time_t seconds;
    seconds = time(NULL);
    streamtime.epoch_ticks = seconds;
    streamtime.zulu_timestamp = ctime(&seconds);
    annotator.__set_annotation_time(streamtime);

    // Setup thrift reading and writing from stdin and stdout
    int input_fd = 0;
    int output_fd = 1;

    // input
    shared_ptr<TFDTransport> innerTransportInput(new TFDTransport(input_fd));
    shared_ptr<TBufferedTransport> transportInput(new TBufferedTransport(innerTransportInput));
    shared_ptr<TBinaryProtocol> protocolInput(new TBinaryProtocol(transportInput));
    transportInput->open();

    // output 
    shared_ptr<TFDTransport> transportOutput(new TFDTransport(output_fd));
    shared_ptr<TBinaryProtocol> protocolOutput(new TBinaryProtocol(transportOutput));
    transportOutput->open();

    // Read and process all stream items
    StreamItem stream_item;
    int cnt=0;
    int matches=0;
    int written=0;

    while (true) {
        try {
            // Read stream_item from stdin
            stream_item.read(protocolInput.get());

            string content;
            string actual_text_source = text_source;
            clog << "Reading stream item content from : " << text_source << endl;
            if (text_source == "clean_visible") {
                content = stream_item.body.clean_visible;
            } else if (text_source == "clean_html") {
                content = stream_item.body.clean_html;
            } else if (text_source == "raw") {
                content = stream_item.body.raw;
            } else {
                cerr << "Bad text_source :" << text_source <<endl;
                exit(-1);
            }

            if (content.size() <= 0) {
                // Fall back to raw if desired text_source has no content.
                content = stream_item.body.raw;
                actual_text_source = "raw";
                if (content.size() <= 0) {
                    // If all applicable text sources are empty, we have a problem and exit with an error
                    cerr << cnt << " Error, doc id: " << stream_item.doc_id << " was empty." << endl;
                    exit(-1);
                }
            }
          
            // Needs fixed.  Removed code here. 
            // nb_matches = search content and return number of matches

            // Count total number of matches
            matches += nb_matches;;

            // For each of the current matches, add a label to the 
            // list of labels.  A label records the character 
            // positions of the match.
            for(int i=0; i< nb_matches; i++) {

                // Get start, end and len of current match
                
                // Add the target identified to the label.  Note this 
                // should be identical to what is in the rating 
                // data we add later.
                vector<string> target_ids(map[num]);

                // Iterator over all 
                for (vector<string>::iterator it = target_ids.begin() ; it != target_ids.end(); ++it) {
                    string target_id(*it); 
                    Target target;
                    target.target_id = target_id;

                    Label label;
                    label.target = target;

                    // Add the actual offsets 
                    Offset offset;
                    offset.type = OffsetType::CHARS;
                    offset.first = start;
                    offset.length = len;
                    offset.content_form = actual_text_source; 
                    label.offsets[OffsetType::CHARS] = offset;
                    label.__isset.offsets = true;

                    // Add new label to the list of labels.
                    stream_item.body.labels[annotatorID].push_back(label);

                    // Here we build up a data structure which maps target id set
                    // of unique text strings which matched.  We later put this
                    // information in a rating object.
                    // target_text_map[target_id].insert(FIX);
                }
            }

            // Add the rating object for each target that matched in a document
            // Reminder:
            // match->first is key
            // match->second is value
            for( unordered_map<string, set<string> >::iterator match=target_text_map.begin(); 
                 match!=target_text_map.end(); 
                 ++match)
            {
                // Construct new rating
                Rating rating;

                // Flag that it contained a mention
                rating.__set_contains_mention(true);

                // Construct a target object for each match
                Target target;
                target.target_id = match->first;
                rating.target = target;

                // Copy all the strings that matched into the mentions field
                copy(match->second.begin(), match->second.end(), back_inserter(rating.mentions));

                // Subtle but vital, we need to do the following for proper serialization.
                rating.__isset.mentions = true;

                // Add the annotator from above.
                rating.annotator = annotator;

                // Push the new rating onto the rating list for this annotator.
                stream_item.ratings[annotatorID].push_back(rating);
            }

            if (not negate) { 
                    // Write stream_item to stdout if it had any ratings
                    if (target_text_map.size() > 0) {
                        stream_item.write(protocolOutput.get());
                        written++;
                    }
            } else if (target_text_map.size() == 0) {
                // Write stream_item to stdout if user requested
                // to show ones that didn't have any matches
                stream_item.write(protocolOutput.get());
                written++;
            }

            // Increment count of stream items processed
            cnt++;
        }
        catch (TTransportException e) {
            // Vital to flush the buffered output or you will lose the last one
            transportOutput->flush();
            clog << "Total stream items processed: " << cnt << endl;
            clog << "Total matches : " << matches << endl;
            clog << "Total stream items written         : " << written << endl;
            if (negate) {
                    clog << " (Note, stream items written were non-matching ones)" << endl;
            }
            break;
        }
    }
    return 0;
}

