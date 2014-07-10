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


CXXFLAGS += -c -g -Wall -fPIC

LDFLAGS += -g -static 

PROGS = jBoincClass test

all: $(PROGS)

libstdc++.a:
	ln -s `g++ -print-file-name=libstdc++.a`

test:
	$(JAVAC) MainTester.java
	$(JAVA) -Djava.library.path=. MainTester

BoincAPIWrapper: libstdc++.a $(BOINC_DIR)/api/libboinc_api.a $(BOINC_LIB_DIR)/libboinc.a
	$(CXX) $(INCLUDES) $(LDFLAGS) boincAPIWrapper.cpp -Wl,-static,--whole-archive  $(BOINC_DIR)/api/libboinc_api.a $(BOINC_LIB_DIR)/libboinc.a -Wl,--no-whole-archive,-Bdynamic -lpthread \
	-shared -o libboincAPIWrapper.so 

libboincAPIWrapper.o:
	$(CXX) $(INCLUDES) $(CXXFLAGS) $(CPPFLAGS) -o libboincAPIWrapper.o boincAPIWrapper.cpp

jBoincAPIWrapper: BoincAPIWrapper
	$(JAVAC) BoincAPIWrapper.java

clean: distclean

distclean:
	/bin/rm -f $(PROGS) *.o *.so *.class *.log

jBoincClass: jBoincAPIWrapper
	$(JAVAC) Boinc.java