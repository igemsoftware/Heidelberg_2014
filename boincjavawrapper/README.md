# Boinc Java Wrapper

The Boinc Java Wrapper is necessary to allow calls from Java to the native Boinc API.

It consists of several files:

1. Boinc.java: Not yet implement. It's supposed to contain the methods that Java developers are supposed to easily call from their code.
2. BoincApiWrapper.java: The Java side of the JNI, a direct translation of the Boinc API to Java code
3. BoincApiWrapper.h: Auto generated file from BoincApiWrapper.java with javah
4. BoincApiWrapper.cpp: The implementation of BoincApiWrapper.h that bridges the method calls to Boinc API
5. MainJava.java: Java program that tests if the implementation works