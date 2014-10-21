# This should work on Linux.  Modify as needed for other platforms.

BOINC_DIR = $(BOINC_HOME)
JDK = $(JAVA_HOME)
JAR=$(JDK)/bin/jar

ifndef ARCH
 $(error ARCH is undefined)
endif
ifndef BOINC_HOME
 $(error BOINC_HOME is undefined)
endif
ifndef JAVA_HOME
 $(error JAVA_HOME is undefined)
endif

all: subdirs jar dynamic-libs

SUBDIRS = src/cpp/libboincAPIWrapper src/java/main/ src/cpp/launcher
     
.PHONY: subdirs $(SUBDIRS)

subdirs: $(SUBDIRS)
     
$(SUBDIRS):
	$(MAKE) -C $@ BOINC_DIR=$(BOINC_DIR) JDK=$(JDK) ARCH=$(ARCH)

jar:
	$(JAR) cvf runtime/jre/lib/ext/igemathome.jar -C build .

dynamic-libs:
	cp src/cpp/libboincAPIWrapper/libboincAPIWrapper.so runtime/jre/lib/$(ARCH)

deploy: all
	cp src/cpp/launcher/launcher deploy
	zip -r deploy/runtime.zip runtime

clean:
	-rm -r build/*
	-for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done
	-rm runtime/jre/lib/$(ARCH)/libboincAPIWrapper.so
	-rm runtime/jre/lib/ext/igemathome.jar
	-rm deploy/launcher
	-rm deploy/runtime.zip
