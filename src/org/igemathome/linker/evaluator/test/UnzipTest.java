package org.igemathome.linker.evaluator.test;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.Enumeration;
import java.util.zip.GZIPInputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Created by Constantin on 30.09.2014.
 */
public class UnzipTest {

    public static void main(String[] args) throws IOException {
        System.out.println("Unzipping Tester");



        String source = "res/zip_test/zip_test.zip";

        ZipFile zf = new ZipFile(source);
        for(Enumeration<? extends ZipEntry> e = zf.entries(); e.hasMoreElements(); ){
            ZipEntry entry = e.nextElement();
            String name = entry.getName();
            if(!entry.isDirectory() && !name.endsWith("_linker.pdb")){
                ZipEntry linker = zf.getEntry(entry.getName().substring(0, name.length()-3));
                // Extract both files and write them to a temporary file, which can easily be parsed
            }

        }

    }

}
