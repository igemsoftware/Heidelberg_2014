package org.igemathome.examples;

import org.igemathome.boinc.wrapper.BoincAPIWrapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

/**
 * This example inits Boinc, writes "Hello Boinc!" to the error stream, waits 5 seconds and finishes
 * Created by artjom on 7/16/14.
 */
public class HelloWorldExample {

    public static void main(String[] args) {
        BoincAPIWrapper.init();

        System.err.println("Hello Boinc!");

        try {
            Thread.sleep(5000);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        }

        BoincAPIWrapper.finish(0);
    }

}
