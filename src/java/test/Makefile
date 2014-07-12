JAVAC = $(JDK)/bin/javac
JAR = $(JDK)/bin/jar

all: test jar

test:
	$(JAVAC) -cp ../ MainTester.java

jar:
	CLASSPATH=..:. $(JAR) cfe MainTest.jar MainTester *.class -C .. org

clean:
	rm *.class *.jar