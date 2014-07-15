
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

LIBS +=\
	-lstdc++

all: launcher

launcher:
	$(CC) -c $(INCLUDES) -DJAVAARCH='"$(ARCH)"' -Wl,-static xmlparser.c launcher.c
	$(CXX) $(INCLUDES) -Wl,-static launcher.o xmlparser.o \
	$(BOINC_ZIP_DIR)/libboinc_zip.a $(BOINC_API_DIR)/libboinc_api.a $(BOINC_LIB_DIR)/libboinc.a \
	-o launcher $(LIBS) -Wl,-Bdynamic -ldl

clean:
	rm launcher