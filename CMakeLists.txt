cmake_minimum_required(VERSION 2.8)

project("Modelling of Cirular Protein Linkers via BOINC")

list( APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
include(AddCompileLinkFlags)

set( BOINC_DIR "$ENV{BOINC_HOME}" CACHE PATH "Path to Boinc Sourcecode" )
set( MANUAL_PATH FALSE CACHE BOOL "Manually select the installation path of the modeller files." )
if(UNIX)
	find_program(MODELLER_EXEC mod9.14)
	if(MODELLER_EXEC AND (NOT MANUAL_PATH))
		set(MODELLER_CFLAGS "")
		set(MODELLER_INCLUDES "")
		message(STATUS "Modeller installation found. Using mod9.14 to get cflags.")
		EXEC_PROGRAM(mod9.14 ARGS --cflags OUTPUT_VARIABLE MODELLER_CFLAGS)
		string(REPLACE "-I" ";" MODELLER_INCLUDES ${MODELLER_CFLAGS})
		list(REMOVE_AT MODELLER_INCLUDES 0)
		include_directories(${MODELLER_INCLUDES})
	else()
		message(WARNING "Modeller installation NOT found! Please set MODELLER_DIR and ARCHETECTURE variables for currect functionality.")
		set(MODELLER_DIR "" CACHE PATH "Path to Modeller installation")
		set(ARCHITECTURE "i386-intel8" CACHE STRING "Select architecture")
		set_property(CACHE ARCHITECTURE PROPERTY STRINGS i386-intel8 i386-absoft rs6000 x86_64-intel8)
		include_directories("${MODELLER_DIR}/src/include" "${MODELLER_DIR}/src/include/${ARCHITECTURE}") # Do some automatisation here
	endif()
else(UNIX)
endif(UNIX)


# use, i.e. don't skip the full RPATH for the build tree
SET(CMAKE_SKIP_BUILD_RPATH  FALSE)

# when building, don't use the install RPATH already
# (but later on when installing)
SET(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE) 

# the RPATH to be used when installing
SET(CMAKE_INSTALL_RPATH "$ORIGIN/lib")

# don't add the automatically determined parts of the RPATH
# which point to directories outside the build tree to the install RPATH
SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH FALSE)


find_package(GLIB2 REQUIRED)
include_directories("${GLIB2_INCLUDE_DIRS}")

add_library( boinc_zip STATIC IMPORTED)
add_library( boinc_api STATIC IMPORTED)
add_library( boinc STATIC IMPORTED)
find_library( modeller_library modeller ${PROJECT_SOURCE_DIR}/lib)

add_executable( circ_modeller ${CMAKE_CURRENT_SOURCE_DIR}/circ_modeller.c )

if(UNIX)
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_zip.a")
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc_api.a")
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.a")

	my_add_link_flags(circ_modeller "-Wl,-rpath-link,${PROJECT_SOURCE_DIR}/lib")
	#set_target_properties( modeller PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/lib/libboinc.a")

	# Find get Architecture and define in Arch.h
	#include(${CMAKE_SOURCE_DIR}/modules/TargetArch.cmake)
	#target_architecture(LINUXLAUNCHER_ARCH)
	#configure_file (
	#	"${CMAKE_CURRENT_SOURCE_DIR}/linux/Arch.h.in"
	#	"${PROJECT_BINARY_DIR}/Arch.h"
	#)
	#include_directories("${PROJECT_BINARY_DIR}")

	set_target_properties( circ_modeller PROPERTIES LINK_FLAGS "-static-libgcc -static-libstdc++")

else(UNIX)
	set_target_properties(boinc_zip PROPERTIES IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/res/libboinc_zip.lib)
	set_target_properties(boinc_api PROPERTIES IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/res/libboinc_api.lib)
	set_target_properties(boinc PROPERTIES IMPORTED_LOCATION "${PROJECT_SOURCE_DIR}/res/libboinc.lib")

endif(UNIX)


target_include_directories( circ_modeller PUBLIC PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ${BOINC_DIR}/lib PUBLIC ${BOINC_DIR}/api PUBLIC ${BOINC_DIR}/zip )
target_link_libraries( circ_modeller ${modeller_library} boinc_zip boinc_api boinc ${GLIB2_LIBRARIES})

install(TARGETS circ_modeller RUNTIME DESTINATION ".")
install(FILES ${PROJECT_SOURCE_DIR}/libs.lib DESTINATION ".")
install(DIRECTORY ${PROJECT_SOURCE_DIR}/lib DESTINATION ".")
install(DIRECTORY ${PROJECT_SOURCE_DIR}/modlib DESTINATION ".")

SET(CPACK_GENERATOR "ZIP")
SET(CPACK_PACKAGE_FILE_NAME "circ_modeller")
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 0)

INCLUDE(CPack)