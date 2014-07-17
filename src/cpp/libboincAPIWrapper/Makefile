
BOINC_API_DIR = $(BOINC_DIR)/api
BOINC_LIB_DIR = $(BOINC_DIR)/lib
BOINC_ZIP_DIR = $(BOINC_DIR)/zip
JDK_INCLUDE_DIR = $(JDK)/include
JDK_INCLUDE_PLATFORM_DIR = $(JDK_INCLUDE_DIR)/linux

INCLUDES += \
	-I$(BOINC_DIR) \
    -I$(BOINC_LIB_DIR) \
    -I$(BOINC_API_DIR) \
    -I$(BOINC_ZIP_DIR) \
    -I$(JDK_INCLUDE_DIR) \
    -I$(JDK_INCLUDE_PLATFORM_DIR)

all: BoincAPIWrapper

libstdc++.a:
	ln -s `g++ -print-file-name=libstdc++.a`

BoincAPIWrapper: libstdc++.a $(BOINC_DIR)/api/libboinc_api.a $(BOINC_LIB_DIR)/libboinc.a
	$(CXX) -fPIC $(INCLUDES) $(LDFLAGS) boincAPIWrapper.cpp -Wl,-static,--whole-archive  $(BOINC_DIR)/api/libboinc_api.a \
	$(BOINC_LIB_DIR)/libboinc.a -Wl,--no-whole-archive,-Bdynamic -lpthread \
	-shared -o libboincAPIWrapper.so

clean:
	rm -r *.so *.a
