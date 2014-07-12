# This should work on Linux.  Modify as needed for other platforms.

BOINC_DIR = $(BOINC_HOME)
JDK = $(JAVA_HOME)
ARCH=i386


all: subdirs

SUBDIRS = src/cpp/libboincAPIWrapper src/java/org/igemathome/boinc src/java/test src/cpp/launcher
     
.PHONY: subdirs $(SUBDIRS)
     
subdirs: $(SUBDIRS)
     
$(SUBDIRS):
	$(MAKE) -C $@ BOINC_DIR=$(BOINC_DIR) JDK=$(JDK) ARCH=$(ARCH)

deploy: subdirs
	cp src/cpp/launcher/launcher deploy
	cp src/cpp/libboincAPIWrapper/libboincAPIWrapper.so deploy/app
	cp src/java/test/MainTest.jar deploy/app

clean:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done
	rm deploy/launcher
	rm deploy/app/*.so deploy/app/*.jar
