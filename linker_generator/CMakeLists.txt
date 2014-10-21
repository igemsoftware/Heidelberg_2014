cmake_minimum_required(VERSION 2.8)

### Windows Comiler flag overrides ###
set(CMAKE_USER_MAKE_RULES_OVERRIDE
   ${CMAKE_SOURCE_DIR}/cmake/c_flag_overrides.cmake)
set(CMAKE_USER_MAKE_RULES_OVERRIDE_CXX
   ${CMAKE_SOURCE_DIR}/cmake/cxx_flag_overrides.cmake)


project("Creation of linkers for circularization of proteins")

list( APPEND CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(AddCompileLinkFlags)

set(CMAKE_CXX_IMPLICIT_LINK_LIBRARIES "") 

set(BUILD_SHARED_LIBS OFF)

set( BOINC_DIR "$ENV{BOINC_HOME}" CACHE PATH "Path to Boinc Sourcecode")

### Python ###
set(Python_ADDITIONAL_VERSIONS 2.7)
find_package(PythonLibs)

### BOINC ###
add_library( boinc_zip STATIC IMPORTED)
add_library( boinc_api STATIC IMPORTED)
add_library( boinc STATIC IMPORTED)

### RPATH settings ###
SET(CMAKE_SKIP_BUILD_RPATH  FALSE)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE) 
SET(CMAKE_INSTALL_RPATH "$ORIGIN")
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)


set(linker_generator_files linker_generator.c temp_exit_wrapper.cpp)
set(linker_generator_libs boinc_zip boinc_api boinc ${PYTHON_LIBRARIES} )
set(linker_generator_includes 	PUBLIC ${PROJECT_SOURCE_DIR}
							PUBLIC ${BOINC_DIR}/zip 
							PUBLIC ${BOINC_DIR}/lib
							PUBLIC ${BOINC_DIR}/api
							PUBLIC ${PYTHON_INCLUDE_DIRS} )

if(UNIX)
	### BOINC ###
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.a")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.a")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.a")

	### Linux specific functions ###
	add_executable( linker_generator ${linker_generator_files} linux_functions.c)
	set(CONFIG_getExecPath "getExecPath_l")
	set(CONFIG_createFailIfExists "createFailIfExists_l")

	### Linking settings ###
	list(APPEND linker_generator_libs pthread m)
	my_add_link_flags(linker_generator "-static-libgcc -static-libstdc++")
	my_add_link_flags(linker_generator "-Wl,-rpath-link,${PROJECT_SOURCE_DIR}/lib")

else(UNIX)
	### BOINC ###
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinczip_staticcrt.lib")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboincapi_staticcrt.lib")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_staticcrt.lib")

	### Windows specific functions ###
	add_executable( linker_generator ${linker_generator_files} windows_functions.c)
	set(CONFIG_getExecPath "getExecPath_w")
	set(CONFIG_createFailIfExists "createFailIfExists_w")

endif(UNIX)

configure_file (
		"${PROJECT_SOURCE_DIR}/config.h.in"
		"${PROJECT_BINARY_DIR}/config.h"
	)

target_include_directories( linker_generator PUBLIC "${PROJECT_BINARY_DIR}" ${linker_generator_includes})

target_link_libraries( linker_generator ${linker_generator_libs})

SET(CPACK_GENERATOR "ZIP")
SET(CPACK_PACKAGE_FILE_NAME "modeller_res")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 0)
set(CPACK_OUTPUT_FILE_PREFIX "deploy")

#add_custom_target(post-packaging COMMAND ${CMAKE_COMMAND} -E message(WARNING "Es funktioniert!") DEPENDS package)
install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${PROJECT_SOURCE_DIR}/lib ${CMAKE_BINARY_DIR}/deploy)")
install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/linker_generator ${CMAKE_BINARY_DIR}/deploy)")


INCLUDE(CPack)
