package org.igemathome.examples;

import org.igemathome.boinc.Boinc;
import org.igemathome.boinc.wrapper.BoincAPIWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/**
 * Reads in the input file input.txt and creates a output file out.txt and converts all letters to
 * uppercase.
 * Created by artjom on 7/16/14.
 */
public class CaseConverterExample {

    public static void main(String[] args) {
        BoincAPIWrapper.init();
        Path input = Paths.get(BoincAPIWrapper.boinc_resolve_filename_s("input.txt"));
        Path out = Paths.get(BoincAPIWrapper.boinc_resolve_filename_s("out.txt"));

        try {
            String inputContent = new String(Files.readAllBytes(input), StandardCharsets.UTF_8);
            String upperCase = inputContent.toUpperCase();
            Files.write(out, upperCase.getBytes(), StandardOpenOption.CREATE);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

    }

}
