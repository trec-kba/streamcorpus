cmake_minimum_required(VERSION 2.6.4)
project (annotation_example)
add_definitions(-DHAVE_NETINET_IN_H)
add_definitions(-DHAVE_INTTYPES_H)

find_path(THRIFT_INCLUDE_DIR protocol/TBinaryProtocol.h
    /opt/local/include
    /usr/local/include
    /usr/include
    )

message(STATUS "Include file detected: [${THRIFT_INCLUDE_DIR}].")


include_directories(${THRIFT_INCLUDE_DIR})
include_directories("../../cpp")
target_link_libraries(streamcorpus)
add_executable(annotation_example annotation_example.cpp)
