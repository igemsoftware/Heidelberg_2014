cmake_minimum_required(VERSION 2.8)

set(CMAKE_USER_MAKE_RULES_OVERRIDE
   ${CMAKE_SOURCE_DIR}/cmake/c_flag_overrides.cmake)
set(CMAKE_USER_MAKE_RULES_OVERRIDE_CXX
   ${CMAKE_SOURCE_DIR}/cmake/cxx_flag_overrides.cmake)

project("Modelling of Cirular Protein Linkers via BOINC")

list( APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(AddCompileLinkFlags)

set(CMAKE_CXX_IMPLICIT_LINK_LIBRARIES "") 

#set(BUILD_SHARED_LIBS OFF)

set( BOINC_DIR "$ENV{BOINC_HOME}" CACHE PATH "Path to Boinc Sourcecode" )


### Python ###
set(Python_ADDITIONAL_VERSIONS 2.7)
find_package(PythonLibs)

### openssl ###
find_package(Crypto REQUIRED)

### BOINC ###
add_library( boinc_zip STATIC IMPORTED)
add_library( boinc_api STATIC IMPORTED)
add_library( boinc STATIC IMPORTED)

### RPATH settings ###
SET(CMAKE_SKIP_BUILD_RPATH  FALSE)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE) 
SET(CMAKE_INSTALL_RPATH "$ORIGIN")
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)


set(circ_modeller_files circ_modeller.c temp_exit_wrapper.cpp)
set(circ_modeller_libs boinc_zip boinc_api boinc ${PYTHON_LIBRARIES} ${CRYPTO_LIBRARIES})

if(UNIX)
	add_executable( circ_modeller ${circ_modeller_files} linux_functions.c)

	### BOINC ###
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.a")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.a")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.a")

	list(APPEND circ_modeller_libs pthread m)
	
	my_add_link_flags(circ_modeller "-static-libgcc -static-libstdc++")

	my_add_link_flags(circ_modeller "-Wl,-rpath-link,${PROJECT_SOURCE_DIR}/lib")

	### Use linux implementation ###
	set(CONFIG_getExecPath "getExecPath_l")
	set(CONFIG_createFailIfExists "createFailIfExists_l")

else(UNIX)
	add_executable( circ_modeller ${circ_modeller_files} windows_functions.c)

	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.lib")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.lib")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.lib")

	set(CONFIG_getExecPath "getExecPath_w")
	set(CONFIG_createFailIfExists "createFailIfExists_w")

endif(UNIX)

configure_file (
		"${CMAKE_CURRENT_SOURCE_DIR}/config.h.in"
		"${PROJECT_BINARY_DIR}/config.h"
	)
include_directories("${PROJECT_BINARY_DIR}")


target_include_directories( circ_modeller 	PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
											PUBLIC ${BOINC_DIR}/zip 
											PUBLIC ${BOINC_DIR}/lib
											PUBLIC ${BOINC_DIR}/api
											PUBLIC ${PYTHON_INCLUDE_DIRS} 
											PUBLIC ${CRYPTO_INCLUDE_DIR})

target_link_libraries( circ_modeller ${circ_modeller_libs})


#install(TARGETS circ_modeller RUNTIME DESTINATION ".")
install(FILES ${PROJECT_SOURCE_DIR}/res/libs.lib DESTINATION ".")
#install(DIRECTORY ${PROJECT_SOURCE_DIR}/lib DESTINATION ".")
install(DIRECTORY ${PROJECT_SOURCE_DIR}/res/modlib DESTINATION ".")

SET(CPACK_GENERATOR "ZIP")
SET(CPACK_PACKAGE_FILE_NAME "modeller_res")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 0)
set(CPACK_OUTPUT_FILE_PREFIX "deploy")

#add_custom_target(post-packaging COMMAND ${CMAKE_COMMAND} -E message(WARNING "Es funktioniert!") DEPENDS package)
install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${PROJECT_SOURCE_DIR}/lib ${CMAKE_BINARY_DIR}/deploy)")
install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/circ_modeller ${CMAKE_BINARY_DIR}/deploy)")


INCLUDE(CPack)
