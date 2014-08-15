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

set( MANUAL_PATH FALSE CACHE BOOL "Manually select the installation path of the modeller files." )

if(UNIX)
	find_program(MODELLER_EXEC mod9.14)
	if(MODELLER_EXEC AND (NOT MANUAL_PATH))
		set(MODELLER_CFLAGS "")
		set(MODELLER_INCLUDES "")
		message(STATUS "Modeller installation found. Using mod9.14 to get cflags.")
		exec_program(mod9.14 ARGS --cflags OUTPUT_VARIABLE MODELLER_CFLAGS)
		string(REPLACE "-I" ";" MODELLER_INCLUDES ${MODELLER_CFLAGS})
		list(REMOVE_AT MODELLER_INCLUDES 0)
		include_directories(${MODELLER_INCLUDES})
	endif()
else(UNIX)
	set(GLIB2_PATH "C:/Users/Max/iGEM/glib-dev_2.28.8-1_win32" CACHE PATH "Path to GLIB2.0-0 Sourcecode")
	include_directories("${GLIB2_PATH}/include/glib-2.0" "${GLIB2_PATH}/lib/glib-2.0/include")
endif(UNIX)


if(NOT MODELLER_EXEC)
	message(WARNING "Modeller installation NOT found! Please set MODELLER_DIR and ARCHETECTURE variables for currect functionality.")
	set(MODELLER_DIR "C:/Program Files (x86)/Modeller9.14" CACHE PATH "Path to Modeller installation")
	set(ARCHITECTURE "i386-intel8" CACHE STRING "Select architecture")
	if(UNIX)
	set_property(CACHE ARCHITECTURE PROPERTY STRINGS i386-intel8 i386-absoft rs6000 x86_64-intel8)
	else()
	set_property(CACHE ARCHITECTURE PROPERTY STRINGS i386-w32 x86_64-w64)
	endif()
	include_directories("${MODELLER_DIR}/src/include" "${MODELLER_DIR}/src/include/${ARCHITECTURE}") # Do some automatisation here
endif()

# use, i.e. don't skip the full RPATH for the build tree
SET(CMAKE_SKIP_BUILD_RPATH  FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE) 

# the RPATH to be used when installing
SET(CMAKE_INSTALL_RPATH "$ORIGIN")

# don't add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)

add_library( boinc_zip STATIC IMPORTED)
add_library( boinc_api STATIC IMPORTED)
add_library( boinc STATIC IMPORTED)


set(circ_modeller_files circ_modeller.c temp_exit_wrapper.cpp)
set(circ_modeller_libs boinc_zip boinc_api boinc)
if(UNIX)
	add_executable( circ_modeller ${circ_modeller_files} linux_functions.c)

	### BOINC ###
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.a")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.a")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.a")

	### Modeller requirements ###
	find_package(GLIB2 REQUIRED)
	include_directories("${GLIB2_INCLUDE_DIRS}")
	find_library( modeller_library modeller ${PROJECT_SOURCE_DIR}/lib)
	list(APPEND circ_modeller_libs ${modeller_library} ${GLIB2_LIBRARIES} pthread m)
	
	#set_target_properties( modeller PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/lib/libboinc.a")

	# Find get Architecture and define in Arch.h
	
	my_add_link_flags(circ_modeller "-static-libgcc -static-libstdc++")

	my_add_link_flags(circ_modeller "-Wl,-rpath-link,${PROJECT_SOURCE_DIR}/lib")
	#set_target_properties( circ_modeller PROPERTIES LINK_FLAGS "-static-libgcc -static-libstdc++")

	### Use linux implementation ###
	set(CONFIG_getExecPath "getExecPath_l")
	set(CONFIG_createFailIfExists "createFailIfExists_l")

else(UNIX)
	add_executable( circ_modeller ${circ_modeller_files} windows_functions.c)

	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.lib")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.lib")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.lib")

	find_library( modeller_library libmodeller10 ${PROJECT_SOURCE_DIR}/lib)
	add_library( glib2_library MODULE IMPORTED)
	set_target_properties( glib2_library PROPERTIES IMPORTED_LOCATION "${GLIB2_PATH}/lib/glib-2.0.lib")
	#find_library( glib2_library "libglib-2.0-0" ${PROJECT_SOURCE_DIR}/lib)
	list(APPEND circ_modeller_libs ${modeller_library} glib2_library)

	set(CONFIG_getExecPath "getExecPath_w")
	set(CONFIG_createFailIfExists "createFailIfExists_w")

endif(UNIX)

configure_file (
		"${CMAKE_CURRENT_SOURCE_DIR}/config.h.in"
		"${PROJECT_BINARY_DIR}/config.h"
	)
include_directories("${PROJECT_BINARY_DIR}")


target_include_directories( circ_modeller PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} PUBLIC ${BOINC_DIR}/zip PUBLIC ${BOINC_DIR}/lib PUBLIC ${BOINC_DIR}/api)
target_link_libraries( circ_modeller ${circ_modeller_libs} )

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
