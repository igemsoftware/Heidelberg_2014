# This should work on Linux.  Modify as needed for other platforms.

BOINC_DIR = $(BOINC_HOME)
BOINC_API_DIR = $(BOINC_DIR)/api
BOINC_LIB_DIR = $(BOINC_DIR)/lib
BOINC_ZIP_DIR = $(BOINC_DIR)/zip
FREETYPE_DIR = /usr/include/freetype2
JDK = $(JAVA_HOME)
JDK_INCLUDE_DIR = $(JDK)/include
JDK_INCLUDE_PLATFORM_DIR = $(JDK_INCLUDE_DIR)/linux
JAVAC = $(JDK)/bin/javac
JAVA = $(JDK)/bin/java

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


CXXFLAGS += -g -Wall

LDFLAGS += -shared -fPIC

PROGS = jBoincClass test

all: $(PROGS)

test:
	$(JAVAC) MainTester.java
	$(JAVA) -Djava.library.path=. MainTester

BoincAPIWrapper:
	$(CXX) $(INCLUDES) $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) -o libboincAPIWrapper.so boincAPIWrapper.cpp

jBoincAPIWrapper: BoincAPIWrapper
	$(JAVAC) BoincAPIWrapper.java

clean: distclean

distclean:
	/bin/rm -f $(PROGS) *.o *.so *.class

jBoincClass: jBoincAPIWrapper
	$(JAVAC) Boinc.java