package org.igemathome.examples;


import org.igemathome.wrapper.BoincAPIWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

/**
 * Created by artjom on 7/16/14.
 */
public class SimpleAlignmentExample {

    public static void main(String[] args) {
        System.err.println("Welcome to my implementation of Smith-Waterman on Boinc");
        BoincAPIWrapper.init();
        System.err.println("After boinc init");
        Path input = Paths.get(BoincAPIWrapper.resolveFilename("input.txt"));
        Path out = Paths.get(BoincAPIWrapper.resolveFilename("out.txt"));

        try {
            String[] inputContent = new String(Files.readAllBytes(input), StandardCharsets.UTF_8).split("\n");
            if (inputContent.length != 2) {
                System.err.println("input has wrong format! It contained: ");
                for (String s : inputContent) {
                    System.err.println(s);
                }
                BoincAPIWrapper.finish(1);
            }
            String l1 = inputContent[0];
            String l2 = inputContent[1];

            SmithWaterman sw = new SmithWaterman(l1, l2);
            System.err.println(l1);
            System.err.println(l2);
            System.err.println(sw.bestAlign());

            Files.write(out, (l1 + "\n" + l2 + "\n" + sw.bestAlign()).getBytes(), StandardOpenOption.CREATE);
        } catch (IOException ex) {
            ex.printStackTrace();
        }


        System.err.println("Finished Alignment");
        BoincAPIWrapper.finish(0);
    }

}