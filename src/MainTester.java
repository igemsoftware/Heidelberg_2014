
import org.igemathome.boinc.wrapper.BoincAPIWrapper;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class MainTester {

    public static void main(String[] args) throws IOException {
        BoincAPIWrapper.init();
        System.err.println("Called BoincAPIWrapper.init()");

        String initDataString = BoincAPIWrapper.getInitData().toString();
        String inputText = readFile(BoincAPIWrapper.boinc_resolve_filename_s("input.txt"));

        System.err.println(inputText);


        try {
            String out = BoincAPIWrapper.boinc_resolve_filename_s("out.txt");
            Path file = Files.createFile(Paths.get(out));
            System.err.println("Boinc resolve filename: " + out);
            System.err.println("Real path: " + file.toRealPath(LinkOption.NOFOLLOW_LINKS));
            Files.write(file, "I'm a text and this is cool".getBytes(), StandardOpenOption.CREATE);
        } catch (IOException e) {
            System.err.println("Exception :" + e.getStackTrace());
        }

        try {
            Thread.sleep(5000);
		} catch(InterruptedException ex) {
		    Thread.currentThread().interrupt();
		}

        System.err.println("Calling BoincAPIWrapper.finish(0)");
        BoincAPIWrapper.finish(0);
	}

    private static String readFile(String filename) throws IOException {
        String everything = "";
        try {
            Path p = Paths.get(filename);
            everything = new String(Files.readAllBytes(p), StandardCharsets.UTF_8);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        return everything;
    }

}
