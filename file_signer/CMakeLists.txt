cmake_minimum_required(VERSION 2.8)

project("Modelling of Cirular Protein Linkers via BOINC")

list( APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(AddCompileLinkFlags)

#set(CMAKE_CXX_IMPLICIT_LINK_LIBRARIES "") 

#set(BUILD_SHARED_LIBS OFF)

### openssl ###
find_package(Crypto REQUIRED)

set(file_signer_files file_signer.c)
set(file_signer_libs ${CRYPTO_LIBRARIES})


add_executable( file_signer ${file_signer_files})




target_include_directories( file_signer 	PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
											PUBLIC ${CRYPTO_INCLUDE_DIR})

target_link_libraries( file_signer ${file_signer_libs})

