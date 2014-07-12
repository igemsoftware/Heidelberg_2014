
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

all: launcher

launcher:
	$(CC) $(INCLUDES) -DJAVAARCH='"$(ARCH)"' -ldl xmlparser.c launcher.c -o launcher

clean:
	rm launcher