# This should work on Linux.  Modify as needed for other platforms.

BOINC_DIR = $(BOINC_HOME)
BOINC_API_DIR = $(BOINC_DIR)/api
BOINC_LIB_DIR = $(BOINC_DIR)/lib
BOINC_ZIP_DIR = $(BOINC_DIR)/zip
FREETYPE_DIR = /usr/include/freetype2
JDK_INCLUDE_DIR = /opt/jdk8/include
JDK_INCLUDE_PLATFORM_DIR = /opt/jdk8/include/linux

INCLUDES += \
	-I$(BOINC_DIR) \
    -I$(BOINC_LIB_DIR) \
    -I$(BOINC_API_DIR) \
    -I$(BOINC_ZIP_DIR) \
    -I$(FREETYPE_DIR) \
    -I$(JDK_INCLUDE_DIR) \
    -I$(JDK_INCLUDE_PLATFORM_DIR) \

CCFLAGS += -c \
	-DJAVAARCH="i386" \


CXXFLAGS += -g \
	-Wall -W -Wshadow -Wpointer-arith -Wcast-qual -Wcast-align -Wwrite-strings -fno-common \
    -L.

LDFLAGS += -shared -fPIC 

PROGS = jBoincClass

all: $(PROGS)

BoincAPIWrapper:
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) -o libboincAPIWrapper.so boincAPIWrapper.cpp

jBoincAPIWrapper: BoincAPIWrapper
	javac BoincAPIWrapper.java

clean: distclean

distclean:
	/bin/rm -f $(PROGS) *.o *.so

jBoincClass: jBoincAPIWrapper
	javac Boinc.java