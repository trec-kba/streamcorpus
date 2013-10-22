cmake_minimum_required(VERSION 2.6.4)
project (annotation_example)
add_definitions(-DHAVE_NETINET_IN_H)
add_definitions(-DHAVE_INTTYPES_H)

set(CMAKE_CXX_FLAGS "-std=c++0x")

find_package( Boost REQUIRED COMPONENTS filesystem program_options system regex)
find_library( THRIFT thrift )
find_path(THRIFT_INCLUDE_DIR protocol/TBinaryProtocol.h
    /opt/local/include
    /usr/local/include
    /usr/include
    /usr/local/include/thrift
    )
message(STATUS "Include file detected: [${THRIFT_INCLUDE_DIR}].")

include_directories(${THRIFT_INCLUDE_DIR})
include_directories(${Boost_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../cpp)

add_executable(annotation_example annotation_example.cpp)
target_link_libraries(annotation_example  ${Boost_LIBRARIES} ${THRIFT} ${CMAKE_CURRENT_SOURCE_DIR}/../../cpp/libstreamcorpus.a)
